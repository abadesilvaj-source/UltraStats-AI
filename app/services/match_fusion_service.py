from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
import json
import re
import unicodedata
from typing import Any, Iterable, Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Competition, Match, Team
from ultrastats_ai.infrastructure.database.models import (
    FusionResultRecord,
    IdentityDecisionRecord,
)
from ultrastats_ai.infrastructure.providers import SourceObservation


TERMINAL = {"finished", "cancelled", "postponed"}


@dataclass(frozen=True, slots=True)
class MatchContribution:
    provider: str
    external_id: str
    kickoff_at: datetime
    home_name: str
    away_name: str
    competition: str
    status: str | None
    home_score: int | None
    away_score: int | None
    venue: str | None
    observed_at: datetime


class MatchFusionService:
    """Concilia partidas e escolhe autoridade por campo, não por API."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def fuse(
        self,
        observations: Iterable[SourceObservation],
        *,
        football_data_payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        contributions = [
            item
            for observation in observations
            if (item := self._adapt(observation)) is not None
        ]
        if football_data_payload:
            contributions.extend(self._football_data(football_data_payload))

        grouped: dict[int, list[MatchContribution]] = {}
        counters = {
            "observations": len(contributions),
            "matched": 0,
            "created": 0,
            "unmatched": 0,
            "conflicts": 0,
            "fields_updated": 0,
            "providers": {},
        }
        for contribution in contributions:
            if not self._in_operational_window(contribution.kickoff_at):
                continue
            match, score = self._resolve(contribution)
            if match is None:
                match = self._create_canonical(contribution)
                counters["created"] += 1
                score = 1.0
            else:
                counters["matched"] += 1
            self._save_identity(contribution, match, score)
            grouped.setdefault(match.id, []).append(contribution)
            provider_stats = counters["providers"].setdefault(
                contribution.provider,
                {"observations": 0, "matched": 0, "fields_selected": 0},
            )
            provider_stats["observations"] += 1
            provider_stats["matched"] += 1

        for match_id, items in grouped.items():
            match = self.session.get(Match, match_id)
            if match is None:
                continue
            result = self._fuse_match(match, items)
            counters["conflicts"] += len(result["conflicts"])
            counters["fields_updated"] += len(result["values"])
            for provider in result["provenance"].values():
                counters["providers"][provider]["fields_selected"] += 1
        return counters

    def _fuse_match(
        self, match: Match, items: list[MatchContribution]
    ) -> dict[str, Any]:
        fields: dict[str, list[tuple[MatchContribution, Any]]] = {
            "kickoff_at": [(item, item.kickoff_at) for item in items],
            "status": [(item, item.status) for item in items if item.status],
            "home_score": [
                (item, item.home_score) for item in items
                if item.home_score is not None
            ],
            "away_score": [
                (item, item.away_score) for item in items
                if item.away_score is not None
            ],
            "venue": [(item, item.venue) for item in items if item.venue],
        }
        values: dict[str, Any] = {}
        provenance: dict[str, str] = {}
        provenance_detail: dict[str, Any] = {}
        conflicts: list[dict[str, Any]] = []
        for field, candidates in fields.items():
            if not candidates:
                continue
            selected, value = self._choose(field, candidates)
            values[field] = (
                value.isoformat() if isinstance(value, datetime) else value
            )
            provenance[field] = selected.provider
            provenance_detail[field] = {
                "provider": selected.provider,
                "base_weight": 1.0,
                "decision": "field_consensus_then_recency",
                "observed_at": selected.observed_at.isoformat(),
                "contributors": sorted({item.provider for item, _ in candidates}),
            }
            distinct = {self._comparable(value) for _, value in candidates}
            if len(distinct) > 1:
                conflicts.append({
                    "field": field,
                    "values": {
                        item.provider: (
                            value.isoformat()
                            if isinstance(value, datetime) else value
                        )
                        for item, value in candidates
                    },
                    "selected_provider": selected.provider,
                })

        if "kickoff_at" in values:
            match.kickoff_at = datetime.fromisoformat(values["kickoff_at"])
        for field in ("status", "home_score", "away_score", "venue"):
            if field in values:
                setattr(match, field, values[field])
        self.session.add(
            FusionResultRecord(
                canonical_id=f"match:{match.id}",
                values=values,
                provenance=provenance_detail,
                conflicts=conflicts,
                fused_at=datetime.now(timezone.utc),
            )
        )
        return {
            "values": values,
            "provenance": provenance,
            "conflicts": conflicts,
        }

    def _choose(
        self,
        field: str,
        candidates: list[tuple[MatchContribution, Any]],
    ) -> tuple[MatchContribution, Any]:
        counts = Counter(self._comparable(value) for _, value in candidates)
        most_common, votes = counts.most_common(1)[0]
        if votes > 1:
            agreed = [
                pair for pair in candidates
                if self._comparable(pair[1]) == most_common
            ]
            return max(agreed, key=lambda pair: pair[0].observed_at)
        if field == "status":
            terminal = [
                pair for pair in candidates if pair[1] in TERMINAL
            ]
            if terminal:
                candidates = terminal
        return max(
            candidates,
            key=lambda pair: pair[0].observed_at,
        )

    def _resolve(
        self, item: MatchContribution
    ) -> tuple[Match | None, float]:
        decision = self.session.scalar(
            select(IdentityDecisionRecord).where(
                IdentityDecisionRecord.provider == item.provider,
                IdentityDecisionRecord.external_id
                == f"match:{item.external_id}",
            )
        )
        if decision and decision.candidate_id:
            match_id = int(decision.candidate_id.removeprefix("match:"))
            return self.session.get(Match, match_id), float(decision.score or 1)
        exact = self.session.scalar(
            select(Match).where(
                Match.source == item.provider,
                Match.external_id == item.external_id,
            )
        )
        if exact:
            return exact, 1.0
        candidates = self.session.scalars(
            select(Match).where(
                Match.kickoff_at.between(
                    item.kickoff_at - timedelta(hours=3),
                    item.kickoff_at + timedelta(hours=3),
                )
            )
        ).all()
        best, best_score = None, 0.0
        for match in candidates:
            home = self.session.get(Team, match.home_team_id)
            away = self.session.get(Team, match.away_team_id)
            if not home or not away:
                continue
            direct = (
                self._similarity(item.home_name, home.name)
                + self._similarity(item.away_name, away.name)
            ) / 2
            reverse = (
                self._similarity(item.home_name, away.name)
                + self._similarity(item.away_name, home.name)
            ) / 2
            score = max(direct, reverse * 0.7)
            if score > best_score:
                best, best_score = match, score
        return (best, best_score) if best_score >= 0.78 else (None, best_score)

    def _create_canonical(self, item: MatchContribution) -> Match:
        competition = self.session.scalar(
            select(Competition).where(Competition.name == item.competition)
        )
        if competition is None:
            competition = Competition(
                name=item.competition or "Competição não informada",
                sport="football",
                source=item.provider,
                external_id=f"{item.provider}:{item.competition}",
                active=True,
            )
            self.session.add(competition)
            self.session.flush()
        home = self._team(item.home_name, item.provider)
        away = self._team(item.away_name, item.provider)
        match = Match(
            competition_id=competition.id,
            home_team_id=home.id,
            away_team_id=away.id,
            kickoff_at=item.kickoff_at,
            status=item.status or "scheduled",
            home_score=item.home_score,
            away_score=item.away_score,
            venue=item.venue,
            source="data_fusion",
            external_id=f"{item.provider}:{item.external_id}",
        )
        self.session.add(match)
        self.session.flush()
        return match

    def _team(self, name: str, provider: str) -> Team:
        normalized = self._normalize(name)
        teams = self.session.scalars(select(Team)).all()
        team = next(
            (candidate for candidate in teams
             if self._normalize(candidate.name) == normalized),
            None,
        )
        if team is None:
            team = Team(name=name, source=provider)
            self.session.add(team)
            self.session.flush()
        return team

    def _save_identity(
        self, item: MatchContribution, match: Match, score: float
    ) -> None:
        record = self.session.scalar(
            select(IdentityDecisionRecord).where(
                IdentityDecisionRecord.provider == item.provider,
                IdentityDecisionRecord.external_id
                == f"match:{item.external_id}",
            )
        )
        if record is None:
            record = IdentityDecisionRecord(
                provider=item.provider,
                external_id=f"match:{item.external_id}",
                status="matched",
                reason="Conciliação automática por equipes e horário.",
                decided_at=datetime.now(timezone.utc),
            )
            self.session.add(record)
        record.status = "matched"
        record.candidate_id = f"match:{match.id}"
        record.score = f"{score:.4f}"
        record.evidence = {
            "home": item.home_name,
            "away": item.away_name,
            "kickoff_at": item.kickoff_at.isoformat(),
        }
        record.decided_at = datetime.now(timezone.utc)

    def _adapt(
        self, observation: SourceObservation
    ) -> MatchContribution | None:
        try:
            if observation.provider == "api_football":
                return self._api_football(observation)
            if observation.provider == "openligadb":
                return self._openligadb(observation)
            if observation.provider == "football_data_uk":
                return self._football_data_uk(observation)
            if observation.provider == "thesportsdb":
                return self._thesportsdb(observation)
            if observation.provider == "sportmonks":
                return self._sportmonks(observation)
            if observation.provider == "the_odds_api":
                return self._the_odds_api(observation)
            if observation.provider in {"goal_api", "zafronix"}:
                return self._normalized_fixture(observation)
        except (KeyError, TypeError, ValueError):
            return None
        return None

    def _api_football(
        self, observation: SourceObservation
    ) -> MatchContribution | None:
        row = observation.values
        fixture, teams = row.get("fixture", {}), row.get("teams", {})
        if not fixture or not teams:
            return None
        status_map = {
            "NS": "scheduled", "TBD": "scheduled", "PST": "postponed",
            "CANC": "cancelled", "ABD": "cancelled", "FT": "finished",
            "AET": "finished", "PEN": "finished", "1H": "in_progress",
            "HT": "in_progress", "2H": "in_progress", "ET": "in_progress",
            "LIVE": "in_progress",
        }
        goals = row.get("goals") or {}
        venue = fixture.get("venue") or {}
        return MatchContribution(
            "api_football", str(fixture.get("id")),
            self._datetime(fixture.get("date")),
            str(teams.get("home", {}).get("name") or ""),
            str(teams.get("away", {}).get("name") or ""),
            str(row.get("league", {}).get("name") or ""),
            status_map.get(str(fixture.get("status", {}).get("short"))),
            self._int(goals.get("home")), self._int(goals.get("away")),
            str(venue.get("name") or "") or None,
            observation.observed_at,
        )

    def _normalized_fixture(
        self, observation: SourceObservation
    ) -> MatchContribution | None:
        row = observation.values
        fixture, teams = row.get("fixture", {}), row.get("teams", {})
        if not fixture or not teams:
            return None
        status_map = {
            "NS": "scheduled", "TBD": "scheduled",
            "PST": "postponed", "CANC": "cancelled",
            "ABD": "cancelled", "FT": "finished",
            "AET": "finished", "PEN": "finished",
            "1H": "in_progress", "HT": "in_progress",
            "2H": "in_progress", "ET": "in_progress",
            "LIVE": "in_progress",
        }
        goals = row.get("goals") or {}
        venue = fixture.get("venue") or {}
        return MatchContribution(
            observation.provider,
            str(fixture.get("id") or observation.external_id),
            self._datetime(fixture.get("date")),
            str(teams.get("home", {}).get("name") or ""),
            str(teams.get("away", {}).get("name") or ""),
            str(row.get("league", {}).get("name") or ""),
            status_map.get(
                str(fixture.get("status", {}).get("short"))
            ),
            self._int(goals.get("home")),
            self._int(goals.get("away")),
            str(venue.get("name") or "") or None,
            observation.observed_at,
        )

    def _thesportsdb(
        self, observation: SourceObservation
    ) -> MatchContribution | None:
        row = observation.values
        if not row.get("strHomeTeam") or not row.get("strAwayTeam"):
            return None
        raw_status = str(row.get("strStatus") or "").casefold()
        if raw_status in {"match finished", "finished", "ft"}:
            status = "finished"
        elif raw_status in {"postponed", "cancelled", "canceled"}:
            status = "postponed" if raw_status == "postponed" else "cancelled"
        elif raw_status in {"in progress", "live"}:
            status = "in_progress"
        else:
            status = "scheduled"
        kickoff = (
            row.get("strTimestamp")
            or "T".join(
                (
                    str(row.get("dateEvent") or ""),
                    str(row.get("strTime") or "00:00:00"),
                )
            )
        )
        return MatchContribution(
            "thesportsdb",
            str(row.get("idEvent") or observation.external_id),
            self._datetime(kickoff),
            str(row["strHomeTeam"]),
            str(row["strAwayTeam"]),
            str(row.get("strLeague") or "TheSportsDB"),
            status,
            self._int(row.get("intHomeScore")),
            self._int(row.get("intAwayScore")),
            str(row.get("strVenue") or "") or None,
            observation.observed_at,
        )

    def _sportmonks(
        self, observation: SourceObservation
    ) -> MatchContribution | None:
        row = observation.values
        participants = [
            item for item in (row.get("participants") or [])
            if isinstance(item, dict)
        ]
        home = next(
            (
                item for item in participants
                if (item.get("meta") or {}).get("location") == "home"
            ),
            participants[0] if participants else None,
        )
        away = next(
            (
                item for item in participants
                if (item.get("meta") or {}).get("location") == "away"
            ),
            participants[1] if len(participants) > 1 else None,
        )
        if not home or not away:
            return None
        state = row.get("state") or {}
        state_name = str(
            state.get("short_name") or state.get("name") or ""
        ).casefold()
        if any(token in state_name for token in ("finished", "ft")):
            status = "finished"
        elif any(token in state_name for token in ("live", "inplay")):
            status = "in_progress"
        elif "postpon" in state_name:
            status = "postponed"
        elif "cancel" in state_name:
            status = "cancelled"
        else:
            status = "scheduled"
        scores: dict[int, int] = {}
        for score in row.get("scores") or []:
            if not isinstance(score, dict):
                continue
            participant_id = self._int(score.get("participant_id"))
            goals = self._int((score.get("score") or {}).get("goals"))
            if participant_id is not None and goals is not None:
                scores[participant_id] = goals
        league = row.get("league") or {}
        venue = row.get("venue") or {}
        return MatchContribution(
            "sportmonks",
            str(row.get("id") or observation.external_id),
            self._datetime(row.get("starting_at")),
            str(home.get("name") or ""),
            str(away.get("name") or ""),
            str(league.get("name") or "Sportmonks"),
            status,
            scores.get(self._int(home.get("id"))),
            scores.get(self._int(away.get("id"))),
            str(venue.get("name") or "") or None,
            observation.observed_at,
        )

    def _the_odds_api(
        self, observation: SourceObservation
    ) -> MatchContribution | None:
        row = observation.values
        if not row.get("home_team") or not row.get("away_team"):
            return None
        return MatchContribution(
            "the_odds_api",
            str(row.get("id") or observation.external_id),
            self._datetime(row.get("commence_time")),
            str(row["home_team"]),
            str(row["away_team"]),
            str(row.get("sport_title") or "The Odds API"),
            "scheduled",
            None,
            None,
            None,
            observation.observed_at,
        )

    def _openligadb(
        self, observation: SourceObservation
    ) -> MatchContribution | None:
        row = observation.values
        team1, team2 = row.get("team1", {}), row.get("team2", {})
        if not team1 or not team2:
            return None
        results = row.get("matchResults") or []
        final = next(
            (result for result in results if result.get("resultTypeID") == 2),
            results[-1] if results else {},
        )
        return MatchContribution(
            "openligadb", str(row.get("matchID")),
            self._datetime(row.get("matchDateTimeUTC") or row.get("matchDateTime")),
            str(team1.get("teamName") or ""), str(team2.get("teamName") or ""),
            str(row.get("leagueName") or row.get("leagueShortcut") or "OpenLigaDB"),
            "finished" if row.get("matchIsFinished") else "scheduled",
            self._int(final.get("pointsTeam1")), self._int(final.get("pointsTeam2")),
            str((row.get("location") or {}).get("locationStadium") or "") or None,
            observation.observed_at,
        )

    def _football_data_uk(
        self, observation: SourceObservation
    ) -> MatchContribution | None:
        row = observation.values
        if not row.get("HomeTeam") or not row.get("AwayTeam"):
            return None
        raw_date = str(row["Date"])
        date = next(
            (
                datetime.strptime(raw_date, pattern).replace(
                    tzinfo=timezone.utc
                )
                for pattern in ("%d/%m/%Y", "%d/%m/%y")
                if self._date_matches(raw_date, pattern)
            ),
            None,
        )
        if date is None:
            raise ValueError("Data histórica inválida.")
        return MatchContribution(
            "football_data_uk", observation.external_id, date,
            str(row["HomeTeam"]), str(row["AwayTeam"]),
            str(row.get("Div") or "Football-Data.co.uk"), "finished",
            self._int(row.get("FTHG")), self._int(row.get("FTAG")), None,
            observation.observed_at,
        )

    def _football_data(
        self, payload: Mapping[str, Any]
    ) -> list[MatchContribution]:
        result = []
        status_map = {
            "SCHEDULED": "scheduled", "TIMED": "scheduled",
            "IN_PLAY": "in_progress", "PAUSED": "in_progress",
            "FINISHED": "finished", "POSTPONED": "postponed",
            "CANCELLED": "cancelled", "SUSPENDED": "postponed",
        }
        now = datetime.now(timezone.utc)
        for row in payload.get("matches", []):
            score = ((row.get("score") or {}).get("fullTime") or {})
            result.append(MatchContribution(
                "football_data", str(row.get("id")),
                self._datetime(row.get("utcDate")),
                str(row.get("homeTeam", {}).get("name") or ""),
                str(row.get("awayTeam", {}).get("name") or ""),
                str(row.get("competition", {}).get("name") or "football-data.org"),
                status_map.get(str(row.get("status"))),
                self._int(score.get("home")), self._int(score.get("away")),
                str(row.get("venue") or "") or None, now,
            ))
        return result

    @staticmethod
    def _in_operational_window(value: datetime) -> bool:
        now = datetime.now(timezone.utc)
        aware = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return now - timedelta(days=3) <= aware <= now + timedelta(days=14)

    @staticmethod
    def _datetime(value: Any) -> datetime:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    @staticmethod
    def _date_matches(value: str, pattern: str) -> bool:
        try:
            datetime.strptime(value, pattern)
            return True
        except ValueError:
            return False

    @staticmethod
    def _int(value: Any) -> int | None:
        return int(value) if value not in (None, "") else None

    @classmethod
    def _similarity(cls, left: str, right: str) -> float:
        return SequenceMatcher(None, cls._normalize(left), cls._normalize(right)).ratio()

    @staticmethod
    def _normalize(value: str) -> str:
        plain = unicodedata.normalize("NFKD", value).encode(
            "ascii", "ignore"
        ).decode().casefold()
        return re.sub(r"\b(fc|cf|sc|ac|club|de|the)\b|[^a-z0-9]", "", plain)

    @staticmethod
    def _comparable(value: Any) -> str:
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc).replace(
                second=0, microsecond=0
            ).isoformat()
        return json.dumps(value, sort_keys=True, default=str)
