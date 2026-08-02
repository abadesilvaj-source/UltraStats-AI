from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import os
from typing import Any

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.models import Match
from ultrastats_ai.infrastructure.database.models import (
    FeatureSnapshotRecord,
    IdentityDecisionRecord,
    RawProviderPayloadRecord,
)


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


class PlayerImpactService:
    """Converte dados individuais conhecidos no instante em contexto pré-jogo.

    O serviço é deliberadamente conservador: dados ausentes produzem um contexto
    neutro e o impacto no xG é limitado. Todas as consultas respeitam ``as_of``
    para impedir que informação coletada após a previsão vaze para o modelo.
    """

    feature_set = "player_impact_v1"

    def __init__(self, session: Session) -> None:
        self.session = session
        self._profile_cache: dict[
            datetime, dict[tuple[str, str], dict[str, object]]
        ] = {}

    @staticmethod
    def enabled() -> bool:
        return os.getenv("PLAYER_IMPACT_ENABLED", "true").strip().casefold() in {
            "1", "true", "yes", "on", "sim",
        }

    @staticmethod
    def neutral() -> dict[str, object]:
        return {
            "enabled": False,
            "home_strength": .50,
            "away_strength": .50,
            "home_coverage": 0.0,
            "away_coverage": 0.0,
            "home_absence_impact": 0.0,
            "away_absence_impact": 0.0,
            "home_xg_adjustment": 0.0,
            "away_xg_adjustment": 0.0,
            "home_lineup_status": "unknown",
            "away_lineup_status": "unknown",
            "home_key_absences": [],
            "away_key_absences": [],
            "players_profiled": 0,
            "confidence": 0.0,
        }

    def context(
        self,
        match: Match,
        *,
        as_of: datetime | None = None,
        persist: bool = False,
    ) -> dict[str, object]:
        if not self.enabled() or not self._tables_available():
            return self.neutral()
        cutoff = self._aware(as_of or datetime.now(timezone.utc))
        # Para partidas históricas, nunca aceite observações posteriores ao
        # início. Para partidas futuras, use apenas o conhecimento atual.
        kickoff = self._aware(match.kickoff_at)
        cutoff = min(cutoff, kickoff)
        fixture_id = self._fixture_id(match)
        team_ids = self._external_team_ids(fixture_id, cutoff)
        if not fixture_id or not all(team_ids):
            return self.neutral()

        profiles = self._player_profiles(cutoff)
        lineups = self._lineups(fixture_id, cutoff)
        absences = self._absences(fixture_id, cutoff)
        home = self._team_context(team_ids[0], profiles, lineups, absences)
        away = self._team_context(team_ids[1], profiles, lineups, absences)
        max_adjustment = _number(
            os.getenv("PLAYER_IMPACT_MAX_XG_ADJUSTMENT", ".12"), .12
        )
        max_adjustment = _bounded(max_adjustment, 0.0, .25)
        minimum_coverage = _bounded(_number(
            os.getenv("PLAYER_IMPACT_MIN_COVERAGE", ".45"), .45
        ))

        def adjustment(team: dict[str, object]) -> float:
            coverage = float(team["coverage"])
            if coverage < minimum_coverage:
                return 0.0
            strength_signal = (float(team["strength"]) - .50) * .16
            absence_penalty = float(team["absence_impact"]) * .60
            return max(
                -max_adjustment,
                min(max_adjustment, strength_signal - absence_penalty),
            ) * coverage

        result: dict[str, object] = {
            "enabled": True,
            "home_strength": home["strength"],
            "away_strength": away["strength"],
            "home_coverage": home["coverage"],
            "away_coverage": away["coverage"],
            "home_absence_impact": home["absence_impact"],
            "away_absence_impact": away["absence_impact"],
            "home_xg_adjustment": adjustment(home),
            "away_xg_adjustment": adjustment(away),
            "home_lineup_status": home["lineup_status"],
            "away_lineup_status": away["lineup_status"],
            "home_key_absences": home["key_absences"],
            "away_key_absences": away["key_absences"],
            "players_profiled": len(profiles),
            "confidence": round(
                (float(home["coverage"]) + float(away["coverage"])) / 2, 4
            ),
            "cutoff": cutoff.isoformat(),
        }
        if persist:
            self._persist(match, cutoff, result)
        return result

    def _tables_available(self) -> bool:
        inspector = inspect(self.session.connection())
        return inspector.has_table(RawProviderPayloadRecord.__tablename__)

    def _fixture_id(self, match: Match) -> str | None:
        if match.source == "api_football" and match.external_id:
            return str(match.external_id).split(":", 1)[0]
        decision = self.session.scalar(
            select(IdentityDecisionRecord)
            .where(
                IdentityDecisionRecord.provider == "api_football",
                IdentityDecisionRecord.candidate_id == f"match:{match.id}",
                IdentityDecisionRecord.status == "matched",
            )
            .order_by(IdentityDecisionRecord.decided_at.desc())
        )
        return (
            str(decision.external_id).removeprefix("match:").split(":", 1)[0]
            if decision is not None else None
        )

    def _external_team_ids(
        self, fixture_id: str | None, cutoff: datetime
    ) -> tuple[str, str]:
        if not fixture_id:
            return "", ""
        row = self.session.scalar(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource.in_(("fixtures", "live_details")),
                RawProviderPayloadRecord.external_id.like(f"{fixture_id}%"),
                RawProviderPayloadRecord.collected_at <= cutoff,
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
        )
        teams = (row.payload.get("teams") or {}) if row else {}
        return (
            str((teams.get("home") or {}).get("id") or ""),
            str((teams.get("away") or {}).get("id") or ""),
        )

    def _player_profiles(self, cutoff: datetime) -> dict[tuple[str, str], dict[str, object]]:
        bucket = cutoff.replace(minute=0, second=0, microsecond=0)
        if bucket in self._profile_cache:
            return self._profile_cache[bucket]
        rows = self.session.scalars(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == "player_statistics",
                RawProviderPayloadRecord.collected_at <= cutoff,
                RawProviderPayloadRecord.collected_at >= cutoff - timedelta(days=365),
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
            .limit(12000)
        ).all()
        aggregate: dict[tuple[str, str], dict[str, Any]] = defaultdict(
            lambda: {
                "name": "", "position": "", "samples": 0, "minutes": 0.0,
                "rating_sum": 0.0, "rating_weight": 0.0, "goals": 0.0,
                "assists": 0.0, "shots_on": 0.0, "key_passes": 0.0,
                "tackles": 0.0, "interceptions": 0.0, "saves": 0.0,
            }
        )
        seen: set[tuple[str, str, str]] = set()
        for row in rows:
            team = row.payload.get("team") or {}
            team_id = str(team.get("id") or "")
            if not team_id:
                continue
            fixture_key = str(row.external_id).split(":", 1)[0]
            for item in row.payload.get("players", ()) or ():
                player = item.get("player") or {}
                player_id = str(player.get("id") or "")
                if not player_id or (fixture_key, team_id, player_id) in seen:
                    continue
                seen.add((fixture_key, team_id, player_id))
                target = aggregate[(team_id, player_id)]
                target["name"] = str(player.get("name") or player_id)
                for stats in item.get("statistics", ()) or ():
                    games = stats.get("games") or {}
                    minutes = _number(games.get("minutes"))
                    rating = _number(games.get("rating"), 6.5)
                    target["position"] = str(games.get("position") or target["position"])
                    target["samples"] += 1
                    target["minutes"] += minutes
                    target["rating_sum"] += rating * max(1.0, minutes)
                    target["rating_weight"] += max(1.0, minutes)
                    target["goals"] += _number((stats.get("goals") or {}).get("total"))
                    target["assists"] += _number((stats.get("goals") or {}).get("assists"))
                    target["shots_on"] += _number((stats.get("shots") or {}).get("on"))
                    target["key_passes"] += _number((stats.get("passes") or {}).get("key"))
                    target["tackles"] += _number((stats.get("tackles") or {}).get("total"))
                    target["interceptions"] += _number((stats.get("tackles") or {}).get("interceptions"))
                    target["saves"] += _number((stats.get("goals") or {}).get("saves"))
        profiles: dict[tuple[str, str], dict[str, object]] = {}
        for key, row in aggregate.items():
            minutes = max(1.0, float(row["minutes"]))
            per90 = 90.0 / minutes
            rating = float(row["rating_sum"]) / max(1.0, float(row["rating_weight"]))
            position = str(row["position"]).casefold()
            production = (
                float(row["goals"]) * 14 + float(row["assists"]) * 10
                + float(row["shots_on"]) * 2 + float(row["key_passes"]) * 1.5
            ) * per90
            defensive = (
                float(row["tackles"]) * 1.4 + float(row["interceptions"]) * 1.8
                + float(row["saves"]) * 2.2
            ) * per90
            if "goalkeeper" in position:
                contribution = defensive
            elif "defender" in position:
                contribution = defensive * .75 + production * .25
            elif "midfielder" in position:
                contribution = defensive * .35 + production * .65
            else:
                contribution = production * .85 + defensive * .15
            importance = _bounded(
                .32 + (rating - 6.0) * .13
                + min(.18, minutes / 1800 * .18)
                + min(.28, contribution / 100),
            ) * 100
            confidence = _bounded(
                min(1.0, int(row["samples"]) / 5) * .55
                + min(1.0, minutes / 450) * .45
            )
            profiles[key] = {
                "player_id": key[1], "name": row["name"],
                "position": row["position"],
                "importance": round(importance, 2),
                "rating": round(rating, 3),
                "minutes": round(minutes, 1),
                "samples": int(row["samples"]),
                "confidence": round(confidence, 4),
            }
        self._profile_cache[bucket] = profiles
        return profiles

    def _lineups(self, fixture_id: str, cutoff: datetime) -> dict[str, set[str]]:
        rows = self.session.scalars(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == "lineups",
                RawProviderPayloadRecord.external_id.like(f"{fixture_id}%"),
                RawProviderPayloadRecord.collected_at <= cutoff,
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
        ).all()
        result: dict[str, set[str]] = {}
        for row in rows:
            team_id = str((row.payload.get("team") or {}).get("id") or "")
            if not team_id or team_id in result:
                continue
            result[team_id] = {
                str((item.get("player") or {}).get("id"))
                for item in row.payload.get("startXI", ()) or ()
                if (item.get("player") or {}).get("id") is not None
            }
        return result

    def _absences(self, fixture_id: str, cutoff: datetime) -> dict[str, set[str]]:
        rows = self.session.scalars(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == "injuries",
                RawProviderPayloadRecord.collected_at <= cutoff,
                RawProviderPayloadRecord.collected_at >= cutoff - timedelta(days=7),
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
            .limit(2000)
        ).all()
        result: dict[str, set[str]] = defaultdict(set)
        for row in rows:
            payload = row.payload
            if str((payload.get("fixture") or {}).get("id") or "") != fixture_id:
                continue
            team_id = str((payload.get("team") or {}).get("id") or "")
            player_id = str((payload.get("player") or {}).get("id") or "")
            if team_id and player_id:
                result[team_id].add(player_id)
        return result

    def _team_context(
        self,
        team_id: str,
        profiles: dict[tuple[str, str], dict[str, object]],
        lineups: dict[str, set[str]],
        absences: dict[str, set[str]],
    ) -> dict[str, object]:
        roster = [row for (candidate, _), row in profiles.items() if candidate == team_id]
        roster.sort(key=lambda row: float(row["importance"]), reverse=True)
        starters = lineups.get(team_id, set())
        selected = (
            [row for row in roster if str(row["player_id"]) in starters]
            if len(starters) >= 7 else roster[:11]
        )
        status = "confirmed" if len(starters) >= 11 else (
            "probable" if len(selected) >= 7 else "unknown"
        )
        reliable = [row for row in selected if float(row["confidence"]) >= .20]
        strength = (
            sum(float(row["importance"]) for row in reliable)
            / max(1, len(reliable)) / 100
            if reliable else .50
        )
        absent = [
            row for row in roster if str(row["player_id"]) in absences.get(team_id, set())
        ]
        absence_impact = min(
            .25,
            sum(float(row["importance"]) for row in absent) / 1100,
        )
        return {
            "strength": round(_bounded(strength), 4),
            "coverage": round(_bounded(len(reliable) / 11), 4),
            "absence_impact": round(absence_impact, 4),
            "lineup_status": status,
            "key_absences": [
                {"player_id": row["player_id"], "name": row["name"],
                 "importance": row["importance"]}
                for row in absent[:5]
            ],
        }

    def _persist(
        self, match: Match, cutoff: datetime, values: dict[str, object]
    ) -> None:
        inspector = inspect(self.session.connection())
        if not inspector.has_table(FeatureSnapshotRecord.__tablename__):
            return
        bucket = cutoff.replace(minute=0, second=0, microsecond=0)
        existing = self.session.scalar(select(FeatureSnapshotRecord).where(
            FeatureSnapshotRecord.entity_type == "match",
            FeatureSnapshotRecord.entity_id == str(match.id),
            FeatureSnapshotRecord.feature_set == self.feature_set,
            FeatureSnapshotRecord.as_of == bucket,
        ))
        provenance = {
            "cutoff": cutoff.isoformat(),
            "policy": "strictly_known_at_cutoff",
            "sources": ["api_football_player_statistics", "lineups", "injuries"],
            "version": 1,
        }
        if existing is None:
            self.session.add(FeatureSnapshotRecord(
                entity_type="match", entity_id=str(match.id),
                feature_set=self.feature_set, values=values,
                provenance=provenance, as_of=bucket,
            ))
        else:
            existing.values = values
            existing.provenance = provenance

    @staticmethod
    def _aware(value: datetime) -> datetime:
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(
            tzinfo=timezone.utc
        )
