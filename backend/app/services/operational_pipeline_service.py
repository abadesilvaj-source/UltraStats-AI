from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from difflib import SequenceMatcher
from math import exp, factorial, lgamma, log
import os
import re
from typing import Any
import unicodedata

from sqlalchemy import func, inspect, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Audit,
    Competition,
    Market,
    Match,
    MatchStatistics,
    Odd,
    Prediction,
    Team,
)
from app.core.football_market_catalog import FOOTBALL_MARKETS
from app.core.competition_catalog import competition_policy
from app.services.post_match_service import PostMatchService
from app.utils.betting_math import (
    calculate_expected_value,
    calculate_implied_probability,
)
from app.utils.odds_matching import best_matching_odd
from ultrastats_ai.domain.prediction import ModelSpecification, PoissonScoreModel
from ultrastats_ai.infrastructure.providers import DataCapability, SourceObservation
from ultrastats_ai.infrastructure.database.models import (
    OddsSnapshotRecord,
    RawProviderPayloadRecord,
)
from ultrastats_ai.infrastructure.database.models import IdentityDecisionRecord


MARKETS = tuple(
    (market.code, market.name, market.category)
    for market in FOOTBALL_MARKETS
)

STATUS_MAP = {
    "NS": "scheduled",
    "TBD": "scheduled",
    "PST": "postponed",
    "CANC": "cancelled",
    "ABD": "cancelled",
    "FT": "finished",
    "AET": "finished",
    "PEN": "finished",
    "1H": "in_progress",
    "HT": "in_progress",
    "2H": "in_progress",
    "ET": "in_progress",
    "BT": "in_progress",
    "P": "in_progress",
    "LIVE": "in_progress",
}


class OperationalPipelineService:
    """Promove observações conciliadas para as tabelas operacionais."""

    model_version = "operational-poisson-v1"

    def __init__(self, session: Session) -> None:
        self.session = session
        self._calibration_history: list[
            tuple[str, float, int, int]
        ] | None = None
        self._market_sample_cache: dict[int, int] = {}

    def process(
        self,
        *,
        fixtures: tuple[SourceObservation, ...],
        odds: tuple[SourceObservation, ...] = (),
    ) -> dict[str, int]:
        counters = {
            "competitions": 0,
            "teams": 0,
            "matches": 0,
            "markets": 0,
            "odds": 0,
            "predictions": 0,
        }
        markets = self._ensure_markets(counters)
        matches: dict[str, Match] = {}
        for observation in fixtures:
            if observation.capability is not DataCapability.FIXTURES:
                continue
            match = self._canonical_match(
                observation.provider, observation.external_id
            )
            # Compatibilidade para bancos mínimos/legados: em produção a
            # fusão cria a identidade canônica antes deste pipeline.
            if (
                match is None
                and observation.provider == "api_football"
            ):
                match = self._promote_fixture(
                    observation.values, counters
                )
            if match is not None:
                matches[
                    f"{observation.provider}:{observation.external_id}"
                ] = match

        self.session.flush()
        counters["odds"] += self._promote_odds(odds, matches, markets)
        self.session.flush()
        for match in matches.values():
            if match.status in {"scheduled", "in_progress"}:
                counters["predictions"] += self._predict(match, markets)
        return counters

    def promote_fixtures_only(
        self, fixtures: tuple[SourceObservation, ...]
    ) -> dict[str, int]:
        """Restaura agenda sem executar o custo preditivo do pipeline completo."""
        counters = {
            "competitions": 0, "teams": 0, "matches": 0,
        }
        promoted = 0
        for observation in fixtures:
            if (
                observation.provider != "api_football"
                or observation.capability is not DataCapability.FIXTURES
            ):
                continue
            if self._canonical_match(
                observation.provider, observation.external_id
            ) is not None:
                continue
            if self._promote_fixture(observation.values, counters) is not None:
                promoted += 1
        self.session.flush()
        return {**counters, "promoted": promoted}

    def reprocess_raw_odds(self, *, limit: int = 5000) -> dict[str, int]:
        """Promove novamente odds brutas após evoluções no catálogo."""
        rows = self.session.scalars(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider.in_(
                    ("api_football", "the_odds_api")
                ),
                RawProviderPayloadRecord.resource == "odds",
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
            .limit(max(1, limit))
        ).all()
        observations = tuple(
            SourceObservation(
                provider=row.provider,
                capability=DataCapability.ODDS,
                external_id=str(row.external_id or ""),
                values=row.payload,
                observed_at=row.collected_at,
            )
            for row in rows
        )
        counters = {"markets": 0}
        markets = self._ensure_markets(counters)
        matches: dict[str, Match] = {}
        for observation in observations:
            if observation.provider != "api_football":
                continue
            fixture = observation.values.get("fixture")
            if not isinstance(fixture, dict) or fixture.get("id") is None:
                continue
            fixture_id = str(fixture["id"])
            match = self._canonical_match("api_football", fixture_id)
            if match is not None:
                matches[f"api_football:{fixture_id}"] = match
        created = self._promote_odds(observations, matches, markets)
        self.session.flush()
        return {
            "payloads": len(observations),
            "matches": len(matches),
            "odds_created": created,
        }

    def process_odds_only(
        self,
        *,
        fixtures: tuple[SourceObservation, ...],
        odds: tuple[SourceObservation, ...],
    ) -> dict[str, int]:
        """Promove preços e atualiza EV sem regenerar modelos probabilísticos."""
        counters = {"markets": 0}
        markets = self._ensure_markets(counters)
        matches: dict[str, Match] = {}
        for observation in fixtures:
            match = self._canonical_match(
                observation.provider, observation.external_id
            )
            if match is not None:
                matches[f"{observation.provider}:{observation.external_id}"] = match
        api_fixture_ids = {
            str(fixture.get("id"))
            for observation in odds
            if observation.provider == "api_football"
            and isinstance(observation.values, dict)
            and isinstance(
                fixture := observation.values.get("fixture"), dict
            )
            and fixture.get("id") is not None
        }
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if api_fixture_ids:
            # Resolver o lote em uma consulta evita milhares de lookups e
            # descarta odds históricas que não podem alimentar o painel atual.
            for match in self.session.scalars(select(Match).where(
                Match.source == "api_football",
                Match.external_id.in_(api_fixture_ids),
                Match.status.in_(("scheduled", "in_progress")),
                Match.kickoff_at >= now - timedelta(hours=6),
                Match.kickoff_at <= now + timedelta(days=14),
            )).all():
                matches[f"api_football:{match.external_id}"] = match
        promotable_odds = tuple(
            observation
            for observation in odds
            if observation.provider != "api_football"
            or (
                isinstance(observation.values, dict)
                and isinstance(observation.values.get("fixture"), dict)
                and f"api_football:{observation.values['fixture'].get('id')}"
                in matches
            )
        )
        collected_after = min(
            (item.observed_at for item in promotable_odds),
            default=datetime.now(timezone.utc),
        ).replace(tzinfo=None) - timedelta(seconds=1)
        created = self._promote_odds(promotable_odds, matches, markets)
        self.session.flush()
        affected_ids = set(self.session.scalars(
            select(Odd.match_id).where(
                Odd.collected_at >= collected_after
            ).distinct()
        ).all())
        updated = self._refresh_prediction_values(affected_ids)
        return {
            "markets": counters["markets"],
            "odds": created,
            "matches_affected": len(affected_ids),
            "predictions": updated,
        }

    def _refresh_prediction_values(self, match_ids: set[int]) -> int:
        if not match_ids:
            return 0
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        maximum_age = float(os.getenv("ODDS_MAX_AGE_HOURS", "6"))
        odds_by_key: dict[tuple[int, int], list[Odd]] = {}
        for odd in self.session.scalars(
            select(Odd).where(Odd.match_id.in_(match_ids))
            .order_by(Odd.collected_at.desc())
        ).all():
            odds_by_key.setdefault((odd.match_id, odd.market_id), []).append(odd)
        updated = 0
        for prediction in self.session.scalars(
            select(Prediction).where(Prediction.match_id.in_(match_ids))
        ).all():
            current = best_matching_odd(
                odds_by_key.get((prediction.match_id, prediction.market_id), ()),
                prediction.selection,
                now=now,
                maximum_age_hours=maximum_age,
            )
            if current is None:
                continue
            prediction.implied_probability = calculate_implied_probability(
                float(current.odd_value)
            )
            prediction.expected_value = calculate_expected_value(
                float(prediction.probability), float(current.odd_value)
            )
            updated += 1
        return updated

    def _canonical_match(
        self, provider: str, external_id: str
    ) -> Match | None:
        decision = None
        if inspect(self.session.connection()).has_table(
            IdentityDecisionRecord.__tablename__
        ):
            decision = self.session.scalar(
                select(IdentityDecisionRecord).where(
                    IdentityDecisionRecord.provider == provider,
                    IdentityDecisionRecord.external_id
                    == f"match:{external_id}",
                    IdentityDecisionRecord.status == "matched",
                )
            )
        if decision and decision.candidate_id:
            return self.session.get(
                Match,
                int(decision.candidate_id.removeprefix("match:")),
            )
        return self.session.scalar(
            select(Match).where(
                Match.source == provider,
                Match.external_id == external_id,
            )
        )

    def process_post_match_statistics(
        self,
        fixture: SourceObservation,
        statistics: tuple[SourceObservation, ...],
    ) -> dict[str, int]:
        """Persiste estatísticas finais e liquida apostas da partida."""
        row = fixture.values
        fixture_data = row.get("fixture", {})
        teams = row.get("teams", {})
        goals = row.get("goals", {})
        external_id = str(fixture_data.get("id", "")).strip()
        home = teams.get("home", {})
        away = teams.get("away", {})
        if (
            not external_id
            or goals.get("home") is None
            or goals.get("away") is None
        ):
            return {"statistics": 0, "settled_bets": 0}
        match = self._canonical_match("api_football", external_id)
        if match is None:
            return {"statistics": 0, "settled_bets": 0}

        by_team = {
            str(item.values.get("team", {}).get("id")): _statistics_values(
                item.values
            )
            for item in statistics
            if isinstance(item.values, dict)
        }
        home_stats = by_team.get(str(home.get("id")), {})
        away_stats = by_team.get(str(away.get("id")), {})
        if not home_stats and not away_stats:
            return {"statistics": 0, "settled_bets": 0}

        result = PostMatchService(self.session).settle_match(
            match_external_id=str(match.external_id),
            home_score=int(goals["home"]),
            away_score=int(goals["away"]),
            source="api_football",
            corners_home=_integer_stat(home_stats, "Corner Kicks"),
            corners_away=_integer_stat(away_stats, "Corner Kicks"),
            yellow_cards_home=_integer_stat(home_stats, "Yellow Cards"),
            yellow_cards_away=_integer_stat(away_stats, "Yellow Cards"),
            red_cards_home=_integer_stat(home_stats, "Red Cards"),
            red_cards_away=_integer_stat(away_stats, "Red Cards"),
            shots_home=_integer_stat(home_stats, "Total Shots"),
            shots_away=_integer_stat(away_stats, "Total Shots"),
            shots_on_target_home=_integer_stat(home_stats, "Shots on Goal"),
            shots_on_target_away=_integer_stat(away_stats, "Shots on Goal"),
            offsides_home=_integer_stat(home_stats, "Offsides"),
            offsides_away=_integer_stat(away_stats, "Offsides"),
            possession_home=_percentage_stat(home_stats, "Ball Possession"),
            possession_away=_percentage_stat(away_stats, "Ball Possession"),
            xg_home=_float_stat(home_stats, "expected_goals"),
            xg_away=_float_stat(away_stats, "expected_goals"),
            commit=False,
        )
        record = self.session.scalar(
            select(MatchStatistics).where(MatchStatistics.match_id == match.id)
        )
        if record is not None:
            for field, value in _extended_fixture_statistics(
                home_stats, away_stats
            ).items():
                if value is not None:
                    setattr(record, field, value)
            record.updated_at = datetime.now()
            self.session.flush()
        return {
            "statistics": 1,
            "settled_bets": len(result["settled_bets"]),
        }

    def process_live_statistics(
        self,
        fixture: SourceObservation,
        statistics: tuple[SourceObservation, ...],
    ) -> int:
        """Atualiza estatísticas parciais sem finalizar ou liquidar a partida."""
        match = self._canonical_match(
            "api_football", str(fixture.external_id)
        )
        teams = fixture.values.get("teams", {})
        if match is None or not teams:
            return 0
        by_team = {
            str(item.values.get("team", {}).get("id")): _statistics_values(
                item.values
            )
            for item in statistics
            if isinstance(item.values, dict)
        }
        home_stats = by_team.get(
            str((teams.get("home") or {}).get("id")), {}
        )
        away_stats = by_team.get(
            str((teams.get("away") or {}).get("id")), {}
        )
        if not home_stats and not away_stats:
            return 0
        values = {
            "corners_home": _integer_stat(home_stats, "Corner Kicks"),
            "corners_away": _integer_stat(away_stats, "Corner Kicks"),
            "yellow_cards_home": _integer_stat(home_stats, "Yellow Cards"),
            "yellow_cards_away": _integer_stat(away_stats, "Yellow Cards"),
            "red_cards_home": _integer_stat(home_stats, "Red Cards"),
            "red_cards_away": _integer_stat(away_stats, "Red Cards"),
            "shots_home": _integer_stat(home_stats, "Total Shots"),
            "shots_away": _integer_stat(away_stats, "Total Shots"),
            "shots_on_target_home": _integer_stat(
                home_stats, "Shots on Goal"
            ),
            "shots_on_target_away": _integer_stat(
                away_stats, "Shots on Goal"
            ),
            "offsides_home": _integer_stat(home_stats, "Offsides"),
            "offsides_away": _integer_stat(away_stats, "Offsides"),
            "possession_home": _percentage_stat(
                home_stats, "Ball Possession"
            ),
            "possession_away": _percentage_stat(
                away_stats, "Ball Possession"
            ),
            "xg_home": _float_stat(home_stats, "expected_goals"),
            "xg_away": _float_stat(away_stats, "expected_goals"),
            **_extended_fixture_statistics(home_stats, away_stats),
        }
        record = self.session.scalar(
            select(MatchStatistics).where(
                MatchStatistics.match_id == match.id
            )
        )
        if record is None:
            record = MatchStatistics(match_id=match.id)
            self.session.add(record)
        for field, value in values.items():
            if value is not None:
                setattr(record, field, value)
        record.updated_at = datetime.now()
        self.session.flush()
        return 1

    def refresh_all_predictions(self) -> int:
        counters = {"markets": 0}
        markets = self._ensure_markets(counters)
        matches = self.session.scalars(
            select(Match).where(
                Match.status.in_(("scheduled", "in_progress")),
                Match.kickoff_at >= (
                    datetime.now(timezone.utc).replace(tzinfo=None)
                    - timedelta(hours=6)
                ),
                Match.kickoff_at <= (
                    datetime.now(timezone.utc).replace(tzinfo=None)
                    + timedelta(days=14)
                ),
            )
        ).all()
        return sum(self._predict(match, markets) for match in matches)

    def _ensure_markets(self, counters: dict[str, int]) -> dict[str, Market]:
        result: dict[str, Market] = {}
        for code, name, category in MARKETS:
            market = self.session.scalar(select(Market).where(Market.code == code))
            if market is None:
                try:
                    with self.session.begin_nested():
                        market = Market(
                            code=code,
                            name=name,
                            category=category,
                            active=True,
                        )
                        self.session.add(market)
                        self.session.flush()
                    counters["markets"] += 1
                except IntegrityError:
                    market = self.session.scalar(
                        select(Market).where(Market.code == code)
                    )
                    if market is None:
                        raise
            result[code] = market
        return result

    def _promote_fixture(
        self,
        row: Any,
        counters: dict[str, int],
    ) -> Match | None:
        if not isinstance(row, dict):
            return None
        fixture = row.get("fixture")
        league = row.get("league")
        teams = row.get("teams")
        if not all(isinstance(value, dict) for value in (fixture, league, teams)):
            return None
        home_data, away_data = teams.get("home"), teams.get("away")
        if not isinstance(home_data, dict) or not isinstance(away_data, dict):
            return None
        external_id = str(fixture.get("id", "")).strip()
        if not external_id:
            return None

        competition = self._competition(league, counters)
        home = self._team(home_data, league, counters)
        away = self._team(away_data, league, counters)
        if home.id == away.id:
            return None
        kickoff = datetime.fromisoformat(str(fixture["date"]).replace("Z", "+00:00"))
        status_data = fixture.get("status") if isinstance(fixture.get("status"), dict) else {}
        goals = row.get("goals") if isinstance(row.get("goals"), dict) else {}
        venue_data = fixture.get("venue") if isinstance(fixture.get("venue"), dict) else {}
        match = self.session.scalar(
            select(Match).where(Match.external_id == external_id)
        )
        if match is None:
            match = Match(
                competition_id=competition.id,
                home_team_id=home.id,
                away_team_id=away.id,
                kickoff_at=kickoff,
                source="api_football",
                external_id=external_id,
            )
            self.session.add(match)
            counters["matches"] += 1
        match.competition_id = competition.id
        match.home_team_id = home.id
        match.away_team_id = away.id
        match.kickoff_at = kickoff
        match.status = STATUS_MAP.get(str(status_data.get("short", "")), "scheduled")
        match.home_score = _optional_int(goals.get("home"))
        match.away_score = _optional_int(goals.get("away"))
        match.venue = str(venue_data.get("name") or "") or None
        return match

    def _competition(self, league: dict[str, Any], counters: dict[str, int]) -> Competition:
        external_id = str(league.get("id"))
        competition = self.session.scalar(
            select(Competition).where(
                Competition.source == "api_football",
                Competition.external_id == external_id,
            )
        )
        if competition is None:
            policy = competition_policy(
                str(league.get("name") or ""),
                str(league.get("country") or "") or None,
            )
            competition = Competition(
                name=(
                    policy.name if policy
                    else str(league.get("name") or f"League {external_id}")
                ),
                country=(
                    policy.country if policy
                    else str(league.get("country") or "") or None
                ),
                season=str(league.get("season") or "") or None,
                sport="football",
                source="api_football",
                external_id=external_id,
                active=True,
            )
            self.session.add(competition)
            self.session.flush()
            counters["competitions"] += 1
        return competition

    def _team(
        self,
        data: dict[str, Any],
        league: dict[str, Any],
        counters: dict[str, int],
    ) -> Team:
        external_id = str(data.get("id"))
        name = str(data.get("name") or f"Team {external_id}")
        team = self.session.scalar(
            select(Team).where(
                Team.source == "api_football",
                Team.external_id == external_id,
            )
        )
        if team is None:
            team = self.session.scalar(select(Team).where(Team.name == name))
        if team is None:
            team = Team(
                name=name,
                country=str(league.get("country") or "") or None,
                league=str(league.get("name") or "") or None,
                source="api_football",
                external_id=external_id,
            )
            self.session.add(team)
            self.session.flush()
            counters["teams"] += 1
        return team

    def _promote_odds(
        self,
        observations: tuple[SourceObservation, ...],
        matches: dict[str, Match],
        markets: dict[str, Market],
    ) -> int:
        created = 0
        existing_keys = {
            (
                match_id,
                market_id,
                bookmaker,
                selection,
                Decimal(str(odd_value)),
            )
            for match_id, market_id, bookmaker, selection, odd_value
            in self.session.execute(
                select(
                    Odd.match_id,
                    Odd.market_id,
                    Odd.bookmaker,
                    Odd.selection,
                    Odd.odd_value,
                )
            ).all()
        }
        snapshot_cutoff = min(
            (self._as_aware_utc(item.observed_at) for item in observations),
            default=datetime.now(timezone.utc),
        ) - timedelta(seconds=1)
        existing_snapshot_keys: set[tuple[str, str, str, str, str, datetime]] = set()
        if inspect(self.session.connection()).has_table(
            OddsSnapshotRecord.__tablename__
        ):
            existing_snapshot_keys = {
                (provider, match_id, bookmaker, market, selection, captured_at)
                for provider, match_id, bookmaker, market, selection, captured_at
                in self.session.execute(select(
                    OddsSnapshotRecord.provider,
                    OddsSnapshotRecord.match_id,
                    OddsSnapshotRecord.bookmaker,
                    OddsSnapshotRecord.market,
                    OddsSnapshotRecord.selection,
                    OddsSnapshotRecord.captured_at,
                ).where(
                    OddsSnapshotRecord.captured_at >= snapshot_cutoff
                )).all()
            }
        for observation in observations:
            if observation.provider == "the_odds_api":
                created += self._promote_the_odds_api(
                    observation, markets, existing_keys,
                    existing_snapshot_keys,
                )
                continue
            if observation.provider != "api_football":
                continue
            row = observation.values
            fixture = row.get("fixture") if isinstance(row, dict) else None
            if not isinstance(fixture, dict):
                continue
            match = matches.get(
                f"{observation.provider}:{fixture.get('id')}"
            )
            if match is None:
                continue
            for bookmaker in row.get("bookmakers", ()):
                if not isinstance(bookmaker, dict):
                    continue
                bookmaker_name = str(bookmaker.get("name") or "unknown")
                for bet in bookmaker.get("bets", ()):
                    if not isinstance(bet, dict):
                        continue
                    for code, selection, value in _mapped_odds(bet):
                        market = markets[code]
                        self._store_odds_snapshot(
                            provider=observation.provider,
                            match_id=match.id,
                            bookmaker=bookmaker_name,
                            market=code,
                            selection=selection,
                            value=value,
                            captured_at=observation.observed_at,
                            existing_keys=existing_snapshot_keys,
                        )
                        key = (
                            match.id,
                            market.id,
                            bookmaker_name,
                            selection,
                            value,
                        )
                        if key not in existing_keys:
                            self.session.add(
                                Odd(
                                    match_id=match.id,
                                    market_id=market.id,
                                    bookmaker=bookmaker_name,
                                    selection=selection,
                                    odd_value=value,
                                    is_closing=False,
                                    collected_at=self._as_naive_utc(
                                        observation.observed_at
                                    ),
                                )
                            )
                            existing_keys.add(key)
                            created += 1
        return created

    def _promote_the_odds_api(
        self,
        observation: SourceObservation,
        markets: dict[str, Market],
        existing_odd_keys: set[tuple[int, int, str, str, Decimal]],
        existing_snapshot_keys: set[
            tuple[str, str, str, str, str, datetime]
        ],
    ) -> int:
        row = observation.values
        match = self._canonical_match(
            observation.provider, observation.external_id
        )
        try:
            kickoff = datetime.fromisoformat(
                str(row["commence_time"]).replace("Z", "+00:00")
            ).replace(tzinfo=None)
        except (KeyError, ValueError):
            return 0
        home_name, away_name = (
            str(row.get("home_team") or ""),
            str(row.get("away_team") or ""),
        )
        if match is None:
            candidates = self.session.scalars(
                select(Match).where(
                    Match.kickoff_at >= kickoff - timedelta(hours=3),
                    Match.kickoff_at <= kickoff + timedelta(hours=3),
                )
            ).all()
            match = next(
                (
                    candidate
                    for candidate in candidates
                    if self._team_similarity(
                        home_name,
                        self.session.get(
                            Team, candidate.home_team_id
                        ).name,
                    ) >= 0.78
                    and self._team_similarity(
                        away_name,
                        self.session.get(
                            Team, candidate.away_team_id
                        ).name,
                    ) >= 0.78
                ),
                None,
            )
        if match is None:
            return 0
        created = 0
        for bookmaker in row.get("bookmakers") or []:
            if not isinstance(bookmaker, dict):
                continue
            bookmaker_name = str(
                bookmaker.get("title") or bookmaker.get("key") or "unknown"
            )
            for market_payload in bookmaker.get("markets") or []:
                for code, selection, value in _mapped_external_odds(
                    market_payload, home_name, away_name
                ):
                    market = markets[code]
                    self._store_odds_snapshot(
                        provider=observation.provider,
                        match_id=match.id,
                        bookmaker=bookmaker_name,
                        market=code,
                        selection=selection,
                        value=value,
                        captured_at=observation.observed_at,
                        existing_keys=existing_snapshot_keys,
                    )
                    key = (
                        match.id, market.id, bookmaker_name,
                        selection, value,
                    )
                    if key not in existing_odd_keys:
                        self.session.add(
                            Odd(
                                match_id=match.id,
                                market_id=market.id,
                                bookmaker=bookmaker_name,
                                selection=selection,
                                odd_value=value,
                                is_closing=False,
                                collected_at=self._as_naive_utc(
                                    observation.observed_at
                                ),
                            )
                        )
                        existing_odd_keys.add(key)
                        created += 1
        return created

    def _store_odds_snapshot(
        self,
        *,
        provider: str,
        match_id: int,
        bookmaker: str,
        market: str,
        selection: str,
        value: Decimal,
        captured_at: datetime,
        existing_keys: set[
            tuple[str, str, str, str, str, datetime]
        ] | None = None,
    ) -> None:
        """Mantém a série temporal usada para movimento, fechamento e CLV."""
        if not inspect(self.session.connection()).has_table(
            OddsSnapshotRecord.__tablename__
        ):
            # Bancos mínimos usados por integrações legadas podem não carregar
            # a base canônica; a promoção da odd continua funcional.
            return
        normalized_capture = self._as_aware_utc(captured_at)
        key = (
            provider, str(match_id), bookmaker, market, selection,
            normalized_capture,
        )
        exists = key in existing_keys if existing_keys is not None else bool(
            self.session.scalar(select(OddsSnapshotRecord.id).where(
                OddsSnapshotRecord.provider == provider,
                OddsSnapshotRecord.match_id == str(match_id),
                OddsSnapshotRecord.bookmaker == bookmaker,
                OddsSnapshotRecord.market == market,
                OddsSnapshotRecord.selection == selection,
                OddsSnapshotRecord.captured_at == normalized_capture,
            ))
        )
        if not exists:
            self.session.add(OddsSnapshotRecord(
                provider=provider,
                match_id=str(match_id),
                bookmaker=bookmaker,
                market=market,
                selection=selection,
                decimal_odds=str(value),
                captured_at=normalized_capture,
            ))
            if existing_keys is not None:
                existing_keys.add(key)

    @staticmethod
    def _team_similarity(left: str, right: str) -> float:
        def normalize(value: str) -> str:
            plain = unicodedata.normalize("NFKD", value).encode(
                "ascii", "ignore"
            ).decode().casefold()
            return re.sub(
                r"\b(fc|cf|sc|ac|club|de|the)\b|[^a-z0-9]",
                "",
                plain,
            )

        return SequenceMatcher(
            None, normalize(left), normalize(right)
        ).ratio()

    @staticmethod
    def _as_naive_utc(value: datetime) -> datetime:
        return (
            value.astimezone(timezone.utc).replace(tzinfo=None)
            if value.tzinfo is not None else value
        )

    @staticmethod
    def _as_aware_utc(value: datetime) -> datetime:
        return (
            value.astimezone(timezone.utc)
            if value.tzinfo is not None
            else value.replace(tzinfo=timezone.utc)
        )

    def _predict(self, match: Match, markets: dict[str, Market]) -> int:
        competition = self.session.get(Competition, match.competition_id)
        if (
            competition is None
            or competition_policy(
                competition.name, competition.country
            ) is None
        ):
            return 0
        home = self.session.get(Team, match.home_team_id)
        away = self.session.get(Team, match.away_team_id)
        if home is None or away is None:
            return 0
        home_xg = max(
            Decimal("0.2"),
            Decimal("1.35") + Decimal(str(home.attack_rating - away.defense_rating)) / 50,
        )
        away_xg = max(
            Decimal("0.2"),
            Decimal("1.10") + Decimal(str(away.attack_rating - home.defense_rating)) / 50,
        )
        # A força global diferencia equipes mesmo quando ataque/defesa ainda
        # têm poucas amostras. O ajuste é simétrico e preserva o mando.
        power_gap = Decimal(str(home.power_rating - away.power_rating))
        home_xg = max(Decimal("0.2"), home_xg + power_gap / Decimal("80"))
        away_xg = max(Decimal("0.2"), away_xg - power_gap / Decimal("80"))
        context = self._match_context(match)
        home_xg = max(
            Decimal("0.2"),
            home_xg * Decimal(str(context["home_attack"]))
            / Decimal(str(context["away_defense"])),
        )
        away_xg = max(
            Decimal("0.2"),
            away_xg * Decimal(str(context["away_attack"]))
            / Decimal(str(context["home_defense"])),
        )
        lineup = self._lineup_context(match)
        provider_context = self._provider_signal_context(match)
        evidence_base = self._evidence_base(match, lineup)
        home_xg = max(
            Decimal("0.2"),
            home_xg + Decimal(
                str((lineup["home_continuity"] - 0.70) * 0.12)
            ),
        )
        away_xg = max(
            Decimal("0.2"),
            away_xg + Decimal(
                str((lineup["away_continuity"] - 0.70) * 0.12)
            ),
        )
        # Desfalques entram como ajuste limitado, nunca como autoridade única.
        # O teto evita que uma fonte isolada desfigure o modelo canônico.
        home_xg = max(
            Decimal("0.2"),
            home_xg - Decimal(str(
                min(.20, provider_context["home_absences"] * .025)
            )),
        )
        away_xg = max(
            Decimal("0.2"),
            away_xg - Decimal(str(
                min(.20, provider_context["away_absences"] * .025)
            )),
        )
        home_xg = max(
            Decimal("0.2"),
            home_xg + Decimal(str(
                max(-.08, min(.08, (
                    float(provider_context["home_player_form"]) - 6.5
                ) * .06))
            )),
        )
        away_xg = max(
            Decimal("0.2"),
            away_xg + Decimal(str(
                max(-.08, min(.08, (
                    float(provider_context["away_player_form"]) - 6.5
                ) * .06))
            )),
        )
        model = PoissonScoreModel(
            ModelSpecification(
                "operational_poisson",
                self.model_version,
                str(match.competition_id),
                "1x2",
                {},
            )
        )
        forecasts = {
            "match_winner": model.predict(home_xg, away_xg, market="1x2").probabilities,
            "over_2_5_goals": {
                "Over 2.5": model.predict(
                    home_xg, away_xg, market="over_under"
                ).probabilities["over"]
            },
            "under_2_5_goals": {
                "Under 2.5": model.predict(
                    home_xg, away_xg, market="over_under"
                ).probabilities["under"]
            },
            "under_3_5_goals": {
                "Under 3.5": min(
                    Decimal("0.92"),
                    model.predict(
                        home_xg, away_xg, market="over_under"
                    ).probabilities["under"] + Decimal(".15"),
                )
            },
            "both_teams_to_score": {
                key.title(): value
                for key, value in model.predict(
                    home_xg, away_xg, market="both_teams_to_score"
                ).probabilities.items()
            },
            "over_8_5_corners": {
                "Over 8.5": Decimal(str(self._negative_binomial_over(
                    8,
                    max(3.0, (home.corner_rating + away.corner_rating)
                        / 10 * context["tempo"]),
                    dispersion=7.0,
                )))
            },
            "over_9_5_corners": {
                "Over 9.5": Decimal(str(self._negative_binomial_over(
                    9,
                    max(3.0, (home.corner_rating + away.corner_rating)
                        / 10 * context["tempo"]),
                    dispersion=7.0,
                )))
            },
            "over_4_5_cards": {
                "Over 4.5": Decimal(str(self._negative_binomial_over(
                    4,
                    max(1.0, (home.card_rating + away.card_rating)
                        / 20 * context["intensity"]),
                    dispersion=4.0,
                )))
            },
        }
        total_goal_lambda = float(home_xg + away_xg)
        home_goal_lambda = float(home_xg)
        away_goal_lambda = float(away_xg)
        total_corner_lambda = max(
            3.0,
            (home.corner_rating + away.corner_rating)
            / 10 * context["tempo"],
        )
        home_corner_lambda = max(
            1.0, home.corner_rating / 10 * context["tempo"]
        )
        away_corner_lambda = max(
            1.0, away.corner_rating / 10 * context["tempo"]
        )
        total_card_lambda = max(
            1.0,
            (home.card_rating + away.card_rating)
            / 20 * context["intensity"],
        )
        home_card_lambda = max(
            .5, home.card_rating / 20 * context["intensity"]
        )
        away_card_lambda = max(
            .5, away.card_rating / 20 * context["intensity"]
        )
        for value in range(0, 6):
            line = f"{value}_5"
            over = Decimal(str(self._poisson_over(
                value, total_goal_lambda
            )))
            forecasts[f"over_{line}_goals"] = {
                f"Over {value}.5": over
            }
            forecasts[f"under_{line}_goals"] = {
                f"Under {value}.5": Decimal("1") - over
            }
        for side, rate in (
            ("home", home_goal_lambda), ("away", away_goal_lambda)
        ):
            for value in range(0, 4):
                line = f"{value}_5"
                over = Decimal(str(self._poisson_over(value, rate)))
                forecasts[f"{side}_over_{line}_goals"] = {
                    f"Over {value}.5": over
                }
                forecasts[f"{side}_under_{line}_goals"] = {
                    f"Under {value}.5": Decimal("1") - over
                }
        for value in range(5, 14):
            line = f"{value}_5"
            over = Decimal(str(self._negative_binomial_over(
                value, total_corner_lambda, dispersion=7.0
            )))
            forecasts[f"over_{line}_corners"] = {
                f"Over {value}.5": over
            }
            forecasts[f"under_{line}_corners"] = {
                f"Under {value}.5": Decimal("1") - over
            }
        for side, rate in (
            ("home", home_corner_lambda), ("away", away_corner_lambda)
        ):
            for value in range(1, 8):
                line = f"{value}_5"
                over = Decimal(str(self._negative_binomial_over(
                    value, rate, dispersion=6.0
                )))
                forecasts[f"{side}_over_{line}_corners"] = {
                    f"Over {value}.5": over
                }
                forecasts[f"{side}_under_{line}_corners"] = {
                    f"Under {value}.5": Decimal("1") - over
                }
        for value in range(0, 9):
            line = f"{value}_5"
            over = Decimal(str(self._negative_binomial_over(
                value, total_card_lambda, dispersion=4.0
            )))
            forecasts[f"over_{line}_cards"] = {
                f"Over {value}.5": over
            }
            forecasts[f"under_{line}_cards"] = {
                f"Under {value}.5": Decimal("1") - over
            }
        for side, rate in (
            ("home", home_card_lambda), ("away", away_card_lambda)
        ):
            for value in range(0, 6):
                line = f"{value}_5"
                over = Decimal(str(self._negative_binomial_over(
                    value, rate, dispersion=3.5
                )))
                forecasts[f"{side}_over_{line}_cards"] = {
                    f"Over {value}.5": over
                }
                forecasts[f"{side}_under_{line}_cards"] = {
                    f"Under {value}.5": Decimal("1") - over
                }
        forecasts["match_winner"] = {
            {"home": "Home", "draw": "Draw", "away": "Away"}[key]: value
            for key, value in forecasts["match_winner"].items()
        }
        provider_winner = provider_context.get("winner_probabilities")
        if isinstance(provider_winner, dict):
            # Sinal externo limitado a 10%; o modelo interno mantém 90%.
            blended_provider = {
                selection: (
                    Decimal("0.90") * forecasts["match_winner"][selection]
                    + Decimal("0.10")
                    * Decimal(str(provider_winner[selection]))
                )
                for selection in ("Home", "Draw", "Away")
            }
            provider_total = sum(blended_provider.values())
            forecasts["match_winner"] = {
                selection: value / provider_total
                for selection, value in blended_provider.items()
            }
        winner = forecasts["match_winner"]
        forecasts["double_chance"] = {
            "Home or Draw": winner["Home"] + winner["Draw"],
            "Home or Away": winner["Home"] + winner["Away"],
            "Draw or Away": winner["Draw"] + winner["Away"],
        }
        decisive = max(
            Decimal(".0001"), winner["Home"] + winner["Away"]
        )
        forecasts["draw_no_bet"] = {
            "Home": winner["Home"] / decisive,
            "Away": winner["Away"] / decisive,
        }
        forecasts["home_clean_sheet"] = {
            "Yes": Decimal(str(exp(-away_goal_lambda))),
            "No": Decimal("1") - Decimal(str(exp(-away_goal_lambda))),
        }
        forecasts["away_clean_sheet"] = {
            "Yes": Decimal(str(exp(-home_goal_lambda))),
            "No": Decimal("1") - Decimal(str(exp(-home_goal_lambda))),
        }
        forecasts["goals_odd_even"] = {
            "Even": Decimal(str(
                (1 + exp(-2 * total_goal_lambda)) / 2
            )),
            "Odd": Decimal(str(
                (1 - exp(-2 * total_goal_lambda)) / 2
            )),
        }
        exact_goals = {
            str(goals): Decimal(str(
                exp(-total_goal_lambda)
                * total_goal_lambda ** goals / factorial(goals)
            ))
            for goals in range(0, 6)
        }
        exact_goals["6+"] = max(
            Decimal("0"), Decimal("1") - sum(exact_goals.values())
        )
        forecasts["exact_total_goals"] = exact_goals
        score_probabilities: dict[str, Decimal] = {}
        covered = Decimal("0")
        for home_score in range(0, 5):
            for away_score in range(0, 5):
                probability = Decimal(str(
                    exp(-home_goal_lambda)
                    * home_goal_lambda ** home_score
                    / factorial(home_score)
                    * exp(-away_goal_lambda)
                    * away_goal_lambda ** away_score
                    / factorial(away_score)
                ))
                score_probabilities[f"{home_score}-{away_score}"] = probability
                covered += probability
        score_probabilities["Other"] = max(
            Decimal("0"), Decimal("1") - covered
        )
        forecasts["correct_score"] = score_probabilities
        market_consensus = self._winner_market_consensus(match, markets)
        if market_consensus:
            consensus, market_weight = market_consensus
            internal_weight = Decimal("1") - market_weight
            # Odds de múltiplas casas são uma fonte independente da força
            # relativa. O blend impede que ratings neutros gerem a mesma
            # recomendação para todos os confrontos.
            blended = {
                selection: (
                    internal_weight * forecasts["match_winner"][selection]
                    + market_weight * consensus[selection]
                )
                for selection in ("Home", "Draw", "Away")
            }
            total = sum(blended.values())
            forecasts["match_winner"] = {
                selection: value / total
                for selection, value in blended.items()
            }
        existing_predictions = {
            (item.market_id, item.selection): item
            for item in self.session.scalars(
                select(Prediction).where(
                    Prediction.match_id == match.id,
                    Prediction.model_version == self.model_version,
                )
            ).all()
        }
        odds_by_market: dict[int, list[Odd]] = {}
        for item in self.session.scalars(
            select(Odd)
            .where(
                Odd.match_id == match.id,
                Odd.odd_value > Decimal("1.00"),
            )
            .order_by(Odd.collected_at.desc())
        ).all():
            odds_by_market.setdefault(item.market_id, []).append(item)
        odds_now = datetime.now(timezone.utc).replace(tzinfo=None)
        maximum_odds_age = float(
            os.getenv("ODDS_MAX_AGE_HOURS", "6")
        )
        created = 0
        for code, selections in forecasts.items():
            market = markets[code]
            evidence = self._market_evidence(
                match,
                market,
                evidence_base,
            )
            for selection, probability in selections.items():
                calibrated_probability = self._calibrate_probability(
                    float(probability), market.id, match.competition_id
                )
                existing = existing_predictions.get(
                    (market.id, selection)
                )
                latest_odd = best_matching_odd(
                    odds_by_market.get(market.id, ()),
                    selection,
                    now=odds_now,
                    maximum_age_hours=maximum_odds_age,
                )
                implied = (
                    calculate_implied_probability(float(latest_odd.odd_value))
                    if latest_odd is not None
                    else None
                )
                expected = (
                    calculate_expected_value(
                        calibrated_probability,
                        float(latest_odd.odd_value),
                    )
                    if latest_odd is not None
                    else None
                )
                lineup_coverage = int(lineup["coverage"])
                confirmed_lineups = int(lineup["confirmed"])
                continuity = (
                    lineup["home_continuity"]
                    + lineup["away_continuity"]
                ) / 2
                evidence_ratio = float(evidence["score"]) / 10
                prediction = existing or Prediction(
                        match_id=match.id,
                        market_id=market.id,
                        selection=selection,
                        model_version=self.model_version,
                    )
                prediction.probability = calibrated_probability
                prediction.implied_probability = implied
                prediction.expected_value = expected
                prediction.confidence = min(
                    0.90,
                    0.42
                    + (0.30 * evidence_ratio)
                    + (0.04 * confirmed_lineups)
                    + (0.04 * continuity),
                )
                prediction.uqs = min(
                    0.88,
                    0.40 + (0.36 * evidence_ratio)
                    + (0.04 * confirmed_lineups),
                )
                prediction.use_score = min(
                    0.88, 0.40 + (0.40 * evidence_ratio)
                )
                prediction.confluence = min(
                    0.90,
                    0.40 + (0.34 * evidence_ratio)
                    + (0.04 * lineup_coverage)
                    + (0.04 * continuity),
                )
                prediction.evidence_level = str(evidence["level"])
                prediction.risk_level = (
                    "low" if evidence["level"] == "high"
                    else "moderate" if evidence["level"] == "medium"
                    else "high"
                )
                if existing is None:
                    self.session.add(prediction)
                    existing_predictions[
                        (market.id, selection)
                    ] = prediction
                    created += 1
        return created

    def _evidence_base(
        self,
        match: Match,
        lineup: dict[str, float | int],
    ) -> dict[str, int]:
        """Mede evidência observável sem privilegiar um provedor."""
        histories = []
        for team_id in (match.home_team_id, match.away_team_id):
            histories.append(int(self.session.scalar(
                select(func.count())
                .select_from(Match)
                .where(
                    Match.status == "finished",
                    Match.kickoff_at < match.kickoff_at,
                    or_(
                        Match.home_team_id == team_id,
                        Match.away_team_id == team_id,
                    ),
                    Match.home_score.is_not(None),
                    Match.away_score.is_not(None),
                )
            ) or 0))
        detailed = int(self.session.scalar(
            select(func.count())
            .select_from(MatchStatistics)
            .join(Match, Match.id == MatchStatistics.match_id)
            .where(
                Match.kickoff_at < match.kickoff_at,
                or_(
                    Match.home_team_id.in_(
                        (match.home_team_id, match.away_team_id)
                    ),
                    Match.away_team_id.in_(
                        (match.home_team_id, match.away_team_id)
                    ),
                ),
            )
        ) or 0)
        bookmakers = int(self.session.scalar(
            select(func.count(func.distinct(Odd.bookmaker)))
            .where(Odd.match_id == match.id)
        ) or 0)
        return {
            "team_history": min(histories) if histories else 0,
            "detailed_history": detailed,
            "bookmakers": bookmakers,
            "lineups": int(lineup["coverage"]),
            "confirmed_lineups": int(lineup["confirmed"]),
        }

    def _market_evidence(
        self,
        match: Match,
        market: Market,
        base: dict[str, int],
    ) -> dict[str, int | str]:
        if market.id not in self._market_sample_cache:
            self._market_sample_cache[market.id] = int(
                self.session.scalar(
                    select(func.count(Audit.id))
                    .join(
                        Prediction,
                        Prediction.id == Audit.prediction_id,
                    )
                    .where(
                        Prediction.market_id == market.id,
                        Audit.result_status.in_(("won", "lost")),
                    )
                ) or 0
            )
        samples = self._market_sample_cache[market.id]
        sample_points = 3 if samples >= 100 else 2 if samples >= 50 else 1 if samples >= 20 else 0
        history = base["team_history"]
        history_points = 2 if history >= 10 else 1 if history >= 5 else 0
        details = base["detailed_history"]
        detail_points = 2 if details >= 10 else 1 if details >= 3 else 0
        price_points = 2 if base["bookmakers"] >= 3 else 1 if base["bookmakers"] else 0
        lineup_points = (
            2 if base["confirmed_lineups"] == 2
            else 1 if base["lineups"] == 2
            else 0
        )
        score = min(
            10,
            sample_points + history_points + detail_points
            + price_points + lineup_points,
        )
        level = "high" if score >= 8 else "medium" if score >= 4 else "low"
        return {
            "level": level,
            "score": score,
            "market_samples": samples,
        }

    def _match_context(self, match: Match) -> dict[str, float]:
        rows = self.session.scalars(
            select(Match).where(
                Match.status == "finished",
                Match.kickoff_at < match.kickoff_at,
                or_(
                    Match.home_team_id.in_(
                        (match.home_team_id, match.away_team_id)
                    ),
                    Match.away_team_id.in_(
                        (match.home_team_id, match.away_team_id)
                    ),
                ),
            ).order_by(Match.kickoff_at.desc()).limit(40)
        ).all()

        def profile(team_id: int) -> tuple[float, float, float]:
            scored = conceded = weights = 0.0
            last_at = None
            for index, row in enumerate(
                item for item in rows
                if team_id in (item.home_team_id, item.away_team_id)
                and item.home_score is not None
                and item.away_score is not None
            ):
                is_home = row.home_team_id == team_id
                opponent = self.session.get(
                    Team,
                    row.away_team_id if is_home else row.home_team_id,
                )
                opponent_factor = (
                    max(.75, min(1.25, float(opponent.power_rating) / 50))
                    if opponent else 1.0
                )
                weight = exp(-index / 8) * opponent_factor
                scored += float(
                    row.home_score if is_home else row.away_score
                ) * weight
                conceded += float(
                    row.away_score if is_home else row.home_score
                ) * weight
                weights += weight
                last_at = last_at or row.kickoff_at
            if not weights:
                return 1.0, 1.0, 7.0
            match_at = self._naive_utc(match.kickoff_at)
            previous_at = self._naive_utc(last_at)
            rest = max(
                2.0,
                (match_at - previous_at).total_seconds() / 86400,
            )
            return (
                max(.65, min(1.45, scored / weights / 1.35)),
                max(.65, min(1.45, conceded / weights / 1.35)),
                rest,
            )

        home_attack, home_defense, home_rest = profile(match.home_team_id)
        away_attack, away_defense, away_rest = profile(match.away_team_id)
        if home_rest < 4:
            home_attack *= .94
        if away_rest < 4:
            away_attack *= .94
        return {
            "home_attack": home_attack,
            "home_defense": home_defense,
            "away_attack": away_attack,
            "away_defense": away_defense,
            "tempo": max(.80, min(1.20, (home_attack + away_attack) / 2)),
            "intensity": max(
                .85, min(1.20, 1 + abs(home_attack - away_attack) * .15)
            ),
        }

    def _provider_signal_context(self, match: Match) -> dict[str, object]:
        """Lê sinais complementares sem conceder prioridade ao provedor."""
        connection = self.session.connection()
        if not inspect(connection).has_table(
            RawProviderPayloadRecord.__tablename__
        ):
            return {
                "home_absences": 0,
                "away_absences": 0,
                "home_player_form": 6.5,
                "away_player_form": 6.5,
                "winner_probabilities": None,
            }
        fixture_id = None
        if match.source == "api_football" and match.external_id:
            fixture_id = str(match.external_id)
        if fixture_id is None:
            decision = self.session.scalar(
                select(IdentityDecisionRecord)
                .where(
                    IdentityDecisionRecord.provider == "api_football",
                    IdentityDecisionRecord.candidate_id
                    == f"match:{match.id}",
                    IdentityDecisionRecord.status == "matched",
                )
                .order_by(IdentityDecisionRecord.decided_at.desc())
            )
            if decision is not None:
                fixture_id = decision.external_id.removeprefix("match:")
        result: dict[str, object] = {
            "home_absences": 0,
            "away_absences": 0,
            "home_player_form": 6.5,
            "away_player_form": 6.5,
            "winner_probabilities": None,
        }
        if not fixture_id:
            return result

        injury_rows = self.session.scalars(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == "injuries",
                RawProviderPayloadRecord.collected_at
                >= datetime.now(timezone.utc) - timedelta(days=2),
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
            .limit(1000)
        ).all()
        seen_players: set[str] = set()
        home_external = away_external = None
        fixture_payload = self.session.scalar(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource.in_(
                    ("fixtures", "live_details")
                ),
                RawProviderPayloadRecord.external_id.like(f"%{fixture_id}%"),
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
        )
        if fixture_payload is not None:
            teams = fixture_payload.payload.get("teams") or {}
            home_external = str((teams.get("home") or {}).get("id") or "")
            away_external = str((teams.get("away") or {}).get("id") or "")
        for row in injury_rows:
            payload = row.payload
            if str((payload.get("fixture") or {}).get("id") or "") != fixture_id:
                continue
            player_id = str((payload.get("player") or {}).get("id") or "")
            if not player_id or player_id in seen_players:
                continue
            seen_players.add(player_id)
            team_id = str((payload.get("team") or {}).get("id") or "")
            if team_id == home_external:
                result["home_absences"] = int(result["home_absences"]) + 1
            elif team_id == away_external:
                result["away_absences"] = int(result["away_absences"]) + 1

        player_rows = self.session.scalars(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == "player_statistics",
                RawProviderPayloadRecord.collected_at
                >= datetime.now(timezone.utc) - timedelta(days=120),
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
            .limit(1500)
        ).all()
        ratings: dict[str, list[float]] = {
            str(home_external or ""): [],
            str(away_external or ""): [],
        }
        for row in player_rows:
            team_id = str((row.payload.get("team") or {}).get("id") or "")
            if team_id not in ratings or len(ratings[team_id]) >= 50:
                continue
            for player in row.payload.get("players", ()) or ():
                for stats in player.get("statistics", ()) or ():
                    rating = (stats.get("games") or {}).get("rating")
                    try:
                        value = float(rating)
                    except (TypeError, ValueError):
                        continue
                    if 0 < value <= 10:
                        ratings[team_id].append(value)
        if home_external and ratings.get(home_external):
            result["home_player_form"] = sum(
                ratings[home_external]
            ) / len(ratings[home_external])
        if away_external and ratings.get(away_external):
            result["away_player_form"] = sum(
                ratings[away_external]
            ) / len(ratings[away_external])

        prediction = self.session.scalar(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == "provider_predictions",
                RawProviderPayloadRecord.external_id.like(f"{fixture_id}%"),
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
        )
        if prediction is not None:
            percentages = (
                (prediction.payload.get("predictions") or {}).get("percent")
                or {}
            )
            try:
                values = {
                    "Home": float(str(percentages["home"]).rstrip("%")) / 100,
                    "Draw": float(str(percentages["draw"]).rstrip("%")) / 100,
                    "Away": float(str(percentages["away"]).rstrip("%")) / 100,
                }
                if sum(values.values()) > 0:
                    total = sum(values.values())
                    result["winner_probabilities"] = {
                        key: value / total for key, value in values.items()
                    }
            except (KeyError, TypeError, ValueError):
                pass
        return result

    @staticmethod
    def _naive_utc(value: datetime) -> datetime:
        """Normaliza timestamps mistos antes de calcular intervalos."""
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _poisson_over(line: int, expected: float) -> float:
        below = sum(
            exp(-expected) * expected ** value / factorial(value)
            for value in range(line + 1)
        )
        return max(.02, min(.98, 1 - below))

    @staticmethod
    def _negative_binomial_over(
        line: int,
        expected: float,
        *,
        dispersion: float,
    ) -> float:
        """Cauda superdispersa para cartões/escanteios.

        Esses eventos variam mais que gols; Poisson subestima as caudas.
        ``dispersion`` alto converge para Poisson.
        """
        mean_value = max(.01, expected)
        shape = max(.1, dispersion)
        probability = shape / (shape + mean_value)
        below = 0.0
        for value in range(line + 1):
            log_pmf = (
                lgamma(value + shape)
                - lgamma(shape)
                - lgamma(value + 1)
                + shape * log(probability)
                + value * log(1 - probability)
            )
            below += exp(log_pmf)
        return max(.02, min(.98, 1 - below))

    def _winner_market_consensus(
        self,
        match: Match,
        markets: dict[str, Market],
    ) -> tuple[dict[str, Decimal], Decimal] | None:
        rows = self.session.scalars(
            select(Odd).where(
                Odd.match_id == match.id,
                Odd.market_id == markets["match_winner"].id,
                Odd.selection.in_(("Home", "Draw", "Away")),
            )
        ).all()
        prices: dict[str, list[Decimal]] = {
            "Home": [], "Draw": [], "Away": []
        }
        for row in rows:
            value = Decimal(str(row.odd_value))
            if value > 1:
                prices[row.selection].append(value)
        if not all(prices.values()):
            return None
        implied = {
            selection: sum(
                (Decimal("1") / value for value in values),
                Decimal("0"),
            ) / len(values)
            for selection, values in prices.items()
        }
        total = sum(implied.values())
        bookmakers = len({row.bookmaker for row in rows})
        market_weight = min(
            Decimal("0.70"),
            Decimal("0.62") + Decimal("0.01") * bookmakers,
        )
        return (
            {
                selection: value / total
                for selection, value in implied.items()
            },
            market_weight,
        )

    def _calibrate_probability(
        self,
        probability: float,
        market_id: int | None = None,
        competition_id: int | None = None,
    ) -> float:
        if self._calibration_history is None:
            self._calibration_history = [
                (status, float(predicted or 0), historical_market, competition)
                for status, predicted, historical_market, competition
                in self.session.execute(
                    select(
                        Audit.result_status,
                        Audit.predicted_probability,
                        Prediction.market_id,
                        Match.competition_id,
                    )
                    .join(
                        Prediction,
                        Prediction.id == Audit.prediction_id,
                    )
                    .join(Match, Match.id == Prediction.match_id)
                    .where(
                        Prediction.model_version
                        == self.model_version,
                        Audit.result_status.in_(("won", "lost")),
                    )
                    .order_by(Audit.audited_at.desc())
                    .limit(1000)
                ).all()
            ]
        nearby = [
            status
            for status, predicted, historical_market, competition
            in self._calibration_history
            if abs(predicted - probability) <= 0.10
            and (market_id is None or historical_market == market_id)
            and (
                competition_id is None or competition == competition_id
            )
        ]
        if len(nearby) < 20 and market_id is not None:
            nearby = [
                status
                for status, predicted, historical_market, _
                in self._calibration_history
                if historical_market == market_id
                and abs(predicted - probability) <= .12
            ]
        if len(nearby) < 20:
            return probability
        observed = sum(
            status == "won" for status in nearby
        ) / len(nearby)
        return (
            observed * len(nearby) + probability * 20
        ) / (len(nearby) + 20)

    def _lineup_coverage(self, match: Match) -> int:
        return int(self._lineup_context(match)["coverage"])

    def _lineup_context(self, match: Match) -> dict[str, float | int]:
        connection = self.session.connection()
        if not inspect(connection).has_table(
            RawProviderPayloadRecord.__tablename__
        ):
            return self._empty_lineup_context()
        provider_ids: dict[str, str] = {}
        if match.source and match.external_id:
            external_id = str(match.external_id)
            if match.source == "data_fusion" and ":" in external_id:
                provider, external_id = external_id.split(":", 1)
                provider_ids[provider] = external_id
            else:
                provider_ids[str(match.source)] = external_id
        for decision in self.session.scalars(
            select(IdentityDecisionRecord).where(
                IdentityDecisionRecord.candidate_id == f"match:{match.id}",
                IdentityDecisionRecord.status == "matched",
            )
        ).all():
            provider_ids[decision.provider] = (
                decision.external_id.removeprefix("match:")
            )
        rows: list[RawProviderPayloadRecord] = []
        for provider, external_id in provider_ids.items():
            rows.extend(self.session.scalars(
                select(RawProviderPayloadRecord)
                .where(
                    RawProviderPayloadRecord.provider == provider,
                    RawProviderPayloadRecord.resource == "lineups",
                    RawProviderPayloadRecord.external_id.like(
                        f"{external_id}%"
                    ),
                )
                .order_by(RawProviderPayloadRecord.collected_at.desc())
            ).all())
        current: dict[
            tuple[str, str],
            tuple[set[str], bool],
        ] = {}
        for row in rows:
            for team_id, starters in self._lineup_teams(
                row.provider, row.payload
            ).items():
                key = (row.provider, team_id)
                if key not in current:
                    current[key] = (starters, len(starters) >= 11)
        continuities: list[float] = []
        for (provider, team_id), (starters, _) in current.items():
            history = self.session.scalars(
                select(RawProviderPayloadRecord)
                .where(
                    RawProviderPayloadRecord.provider == provider,
                    RawProviderPayloadRecord.resource == "lineups",
                )
                .order_by(RawProviderPayloadRecord.collected_at.desc())
                .limit(200)
            ).all()
            previous_starters = next(
                (
                    teams[team_id]
                    for item in history
                    if (
                        teams := self._lineup_teams(
                            item.provider, item.payload
                        )
                    )
                    and team_id in teams
                    and teams[team_id] != starters
                ),
                set(),
            )
            continuities.append(
                len(starters.intersection(previous_starters))
                / max(1, len(starters))
                if previous_starters else 0.70
            )
        while len(continuities) < 2:
            continuities.append(0.70)
        return {
            "coverage": min(2, len(current)),
            "confirmed": min(
                2, sum(item[1] for item in current.values())
            ),
            "home_continuity": continuities[0],
            "away_continuity": continuities[1],
        }

    @staticmethod
    def _lineup_teams(
        provider: str,
        payload: dict[str, Any],
    ) -> dict[str, set[str]]:
        if provider == "api_football":
            team_id = str(payload.get("team", {}).get("id") or "")
            starters = {
                str(item.get("player", {}).get("id"))
                for item in payload.get("startXI", ())
                if item.get("player", {}).get("id") is not None
            }
            return {team_id: starters} if team_id and starters else {}
        grouped: dict[str, set[str]] = {}
        for item in payload.get("lineups", ()) or ():
            if not isinstance(item, dict):
                continue
            team = item.get("team") or {}
            player = item.get("player") or {}
            team_id = str(
                item.get("team_id")
                or item.get("participant_id")
                or (team.get("id") if isinstance(team, dict) else "")
                or ""
            )
            player_id = str(
                item.get("player_id")
                or (player.get("id") if isinstance(player, dict) else "")
                or ""
            )
            if team_id and player_id:
                grouped.setdefault(team_id, set()).add(player_id)
        return grouped

    @staticmethod
    def _empty_lineup_context() -> dict[str, float | int]:
        return {
            "coverage": 0,
            "confirmed": 0,
            "home_continuity": 0.70,
            "away_continuity": 0.70,
        }


def _optional_int(value: Any) -> int | None:
    return int(value) if value is not None else None


def _statistics_values(row: dict[str, Any]) -> dict[str, Any]:
    return {
        str(item.get("type")): item.get("value")
        for item in row.get("statistics", ())
        if isinstance(item, dict) and item.get("type")
    }


def _integer_stat(values: dict[str, Any], key: str) -> int | None:
    value = values.get(key)
    if value in (None, ""):
        return None
    try:
        return int(float(str(value).rstrip("%")))
    except ValueError:
        return None


def _float_stat(values: dict[str, Any], key: str) -> float | None:
    value = values.get(key)
    if value in (None, ""):
        return None
    try:
        return float(str(value).rstrip("%"))
    except ValueError:
        return None


def _percentage_stat(values: dict[str, Any], key: str) -> float | None:
    return _float_stat(values, key)


def _extended_fixture_statistics(
    home: dict[str, Any], away: dict[str, Any]
) -> dict[str, int | float | None]:
    """Mapeia apenas as estatísticas documentadas no feed de partidas.

    Valores ausentes permanecem nulos para que a interface nunca confunda
    indisponibilidade do provedor com um zero esportivo real.
    """
    integer_fields = {
        "shots_off_target": "Shots off Goal",
        "blocked_shots": "Blocked Shots",
        "shots_inside_box": "Shots insidebox",
        "shots_outside_box": "Shots outsidebox",
        "fouls": "Fouls",
        "goalkeeper_saves": "Goalkeeper Saves",
        "passes": "Total passes",
        "passes_accurate": "Passes accurate",
    }
    result: dict[str, int | float | None] = {}
    for field, provider_key in integer_fields.items():
        result[f"{field}_home"] = _integer_stat(home, provider_key)
        result[f"{field}_away"] = _integer_stat(away, provider_key)
    result["pass_accuracy_home"] = _percentage_stat(home, "Passes %")
    result["pass_accuracy_away"] = _percentage_stat(away, "Passes %")
    return result


def _mapped_odds(bet: dict[str, Any]) -> tuple[tuple[str, str, Decimal], ...]:
    name = str(bet.get("name") or "").casefold()
    result: list[tuple[str, str, Decimal]] = []
    for item in bet.get("values", ()):
        if not isinstance(item, dict):
            continue
        try:
            odd = Decimal(str(item["odd"]))
        except (KeyError, ArithmeticError):
            continue
        if odd <= Decimal("1.00"):
            continue
        label = str(item.get("value") or "")
        if name == "match winner" and label in {"Home", "Draw", "Away"}:
            result.append(("match_winner", label, odd))
        elif name == "double chance":
            selection = {
                "Home/Draw": "Home or Draw",
                "Home/Away": "Home or Away",
                "Draw/Away": "Draw or Away",
            }.get(label)
            if selection:
                result.append(("double_chance", selection, odd))
        elif name in {"home/away", "draw no bet"} and label in {
            "Home", "Away"
        }:
            result.append(("draw_no_bet", label, odd))
        elif name in {"goals over/under", "over/under"}:
            mapped = _mapped_total_line(label, "goals", 0, 5)
            if mapped:
                result.append((*mapped, odd))
        elif name in {"both teams score", "both teams to score"} and label in {"Yes", "No"}:
            result.append(("both_teams_to_score", label, odd))
        elif name == "exact goals number":
            selection = "6+" if label in {"more 6", "more 7"} else label
            if selection in {"0", "1", "2", "3", "4", "5", "6+"}:
                result.append(("exact_total_goals", selection, odd))
        elif name == "odd/even" and label in {"Odd", "Even"}:
            result.append(("goals_odd_even", label, odd))
        elif name == "exact score":
            selection = label.replace(":", "-")
            if re.fullmatch(r"[0-4]-[0-4]", selection):
                result.append(("correct_score", selection, odd))
        elif name == "clean sheet - home" and label in {"Yes", "No"}:
            result.append(("home_clean_sheet", label, odd))
        elif name == "clean sheet - away" and label in {"Yes", "No"}:
            result.append(("away_clean_sheet", label, odd))
        elif name == "total - home":
            mapped = _mapped_total_line(label, "goals", 0, 3, "home")
            if mapped:
                result.append((*mapped, odd))
        elif name == "total - away":
            mapped = _mapped_total_line(label, "goals", 0, 3, "away")
            if mapped:
                result.append((*mapped, odd))
        elif name in {"corners over under", "corners over/under"}:
            mapped = _mapped_total_line(label, "corners", 5, 13)
            if mapped:
                result.append((*mapped, odd))
        elif name == "home corners over/under":
            mapped = _mapped_total_line(
                label, "corners", 1, 7, "home"
            )
            if mapped:
                result.append((*mapped, odd))
        elif name == "away corners over/under":
            mapped = _mapped_total_line(
                label, "corners", 1, 7, "away"
            )
            if mapped:
                result.append((*mapped, odd))
        elif name in {"cards over/under", "yellow over/under"}:
            mapped = _mapped_total_line(label, "cards", 0, 8)
            if mapped:
                result.append((*mapped, odd))
        elif name in {"home team total cards", "home team yellow cards"}:
            mapped = _mapped_total_line(label, "cards", 0, 5, "home")
            if mapped:
                result.append((*mapped, odd))
        elif name in {"away team total cards", "away team yellow cards"}:
            mapped = _mapped_total_line(label, "cards", 0, 5, "away")
            if mapped:
                result.append((*mapped, odd))
    return tuple(result)


def _mapped_total_line(
    label: str,
    suffix: str,
    minimum: int,
    maximum: int,
    side: str | None = None,
) -> tuple[str, str] | None:
    match = re.fullmatch(r"(Over|Under) (\d+)\.5", label)
    if match is None:
        return None
    direction, raw_line = match.groups()
    line = int(raw_line)
    if not minimum <= line <= maximum:
        return None
    parts = [
        *([side] if side else []),
        direction.casefold(),
        f"{line}_5",
        suffix,
    ]
    return "_".join(parts), label


def _mapped_external_odds(
    market: dict[str, Any],
    home_name: str,
    away_name: str,
) -> tuple[tuple[str, str, Decimal], ...]:
    key = str(market.get("key") or "")
    result: list[tuple[str, str, Decimal]] = []
    for outcome in market.get("outcomes") or []:
        if not isinstance(outcome, dict):
            continue
        try:
            odd = Decimal(str(outcome["price"]))
        except (KeyError, ArithmeticError):
            continue
        if odd <= Decimal("1.00"):
            continue
        name = str(outcome.get("name") or "")
        point = outcome.get("point")
        if key == "h2h":
            selection = (
                "Home" if name == home_name
                else "Away" if name == away_name
                else "Draw" if name.casefold() == "draw"
                else None
            )
            if selection:
                result.append(("match_winner", selection, odd))
        elif key == "totals" and point is not None:
            try:
                numeric_point = float(point)
            except (TypeError, ValueError):
                continue
            if numeric_point % 1 == 0.5:
                label = f"{name.title()} {numeric_point:.1f}"
                mapped = _mapped_total_line(label, "goals", 0, 5)
                if mapped:
                    result.append((*mapped, odd))
    return tuple(result)
