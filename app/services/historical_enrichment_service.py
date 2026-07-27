from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
import unicodedata

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Team
from ultrastats_ai.infrastructure.database.models import FusionResultRecord
from ultrastats_ai.infrastructure.providers import SourceObservation


class HistoricalEnrichmentService:
    """Transforma resultados históricos complementares em ratings reutilizáveis."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def process(
        self, observations: tuple[SourceObservation, ...]
    ) -> dict[str, int]:
        rows = [
            item for item in observations
            if item.provider == "football_data_uk"
            and item.values.get("HomeTeam")
            and item.values.get("AwayTeam")
        ]
        if not rows:
            return {"rows": 0, "teams_updated": 0, "skipped": 0}
        fingerprint = sha256(
            json.dumps(
                [
                    (item.external_id, item.values.get("FTHG"), item.values.get("FTAG"))
                    for item in rows
                ],
                sort_keys=True,
                default=str,
            ).encode()
        ).hexdigest()
        canonical_id = f"training:football_data_uk:{fingerprint[:32]}"
        if self.session.scalar(
            select(FusionResultRecord.id).where(
                FusionResultRecord.canonical_id == canonical_id
            )
        ):
            return {"rows": len(rows), "teams_updated": 0, "skipped": len(rows)}

        aggregates: dict[str, dict[str, float]] = defaultdict(
            lambda: {"played": 0, "for": 0, "against": 0}
        )
        home_wins = draws = away_wins = valid = 0
        for item in rows:
            try:
                home_goals = int(item.values["FTHG"])
                away_goals = int(item.values["FTAG"])
            except (KeyError, TypeError, ValueError):
                continue
            home = self._normalize(str(item.values["HomeTeam"]))
            away = self._normalize(str(item.values["AwayTeam"]))
            for team, scored, conceded in (
                (home, home_goals, away_goals),
                (away, away_goals, home_goals),
            ):
                aggregates[team]["played"] += 1
                aggregates[team]["for"] += scored
                aggregates[team]["against"] += conceded
            valid += 1
            home_wins += home_goals > away_goals
            draws += home_goals == away_goals
            away_wins += home_goals < away_goals

        teams_updated = 0
        for team in self.session.scalars(select(Team)).all():
            sample = aggregates.get(self._normalize(team.name))
            if not sample or sample["played"] < 3:
                continue
            goals_for = sample["for"] / sample["played"]
            goals_against = sample["against"] / sample["played"]
            team.attack_rating = min(100, max(1, 50 + (goals_for - 1.35) * 18))
            team.defense_rating = min(100, max(1, 50 + (1.35 - goals_against) * 18))
            team.goal_rating = min(
                100, max(1, 50 + ((goals_for + goals_against) - 2.7) * 10)
            )
            teams_updated += 1

        values = {
            "sample_size": valid,
            "home_win_rate": home_wins / valid if valid else 0,
            "draw_rate": draws / valid if valid else 0,
            "away_win_rate": away_wins / valid if valid else 0,
            "teams_updated": teams_updated,
        }
        self.session.add(
            FusionResultRecord(
                canonical_id=canonical_id,
                values=values,
                provenance={
                    field: {
                        "provider": "football_data_uk",
                        "role": "historical_training",
                    }
                    for field in values
                },
                conflicts=[],
                fused_at=datetime.now(timezone.utc),
            )
        )
        return {
            "rows": len(rows),
            "teams_updated": teams_updated,
            "skipped": 0,
        }

    @staticmethod
    def _normalize(value: str) -> str:
        plain = unicodedata.normalize("NFKD", value).encode(
            "ascii", "ignore"
        ).decode().casefold()
        return re.sub(r"\b(fc|cf|sc|ac|club|de|the)\b|[^a-z0-9]", "", plain)
