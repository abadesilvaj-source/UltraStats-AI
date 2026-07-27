from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo
import os

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.models import Bet, Match, MatchStatistics
from app.services.sync_monitor_service import SyncMonitorService
from ultrastats_ai.infrastructure.providers import (
    DataCapability,
    MultiSourceEngine,
    RawProviderPayload,
    SourceObservation,
    build_football_data_provider,
    build_multi_source_engine,
)
from ultrastats_ai.infrastructure.providers.persistence import (
    SqlAlchemyHealthStore,
    SqlAlchemyRawPayloadStore,
)
from ultrastats_ai.infrastructure.database.models import (
    IdentityDecisionRecord,
    LiveEventRecord,
    RawProviderPayloadRecord,
)
from app.services.operational_pipeline_service import OperationalPipelineService
from app.services.match_fusion_service import MatchFusionService
from app.services.historical_enrichment_service import HistoricalEnrichmentService
from app.services.operational_intelligence_service import (
    OperationalIntelligenceService,
)
from app.services.maturity_service import MaturityService
from app.services.post_match_service import PostMatchService
from ultrastats_ai.domain.live import (
    LiveEngine,
    LiveEvent,
    LiveEventType,
    LiveHealth,
    LiveMatchState,
    LivePhase,
    LiveRecommendation,
)
from ultrastats_ai.infrastructure.live import LiveStore


class MultiProviderSyncService:
    """Executa e audita a coleta periódica das fontes reais."""

    def __init__(
        self,
        session: Session,
        *,
        environment: Mapping[str, str] | None = None,
        engine_factory: Callable[[Mapping[str, str]], MultiSourceEngine] = (
            build_multi_source_engine
        ),
        football_factory: Callable[[], object] = build_football_data_provider,
    ) -> None:
        self.session = session
        self.environment = os.environ if environment is None else environment
        self.engine_factory = engine_factory
        self.football_factory = football_factory
        self.monitor = SyncMonitorService(session)
        self.raw_store = SqlAlchemyRawPayloadStore(session)
        self.health_store = SqlAlchemyHealthStore(session)

    def run(self, *, triggered_by: str = "scheduler") -> dict[str, object]:
        sync_run = self.monitor.start_run("multi_provider", triggered_by)
        engine = self.engine_factory(self.environment)
        football_provider = None
        football_data_payload = None
        saved = 0
        skipped = 0
        failures: dict[str, str] = {}

        try:
            for source in engine.sources:
                health = source.health_check()
                self.health_store.save(health)
                if not health.available:
                    failures[source.name] = health.message

            parameters = self._fixture_parameters()
            report = engine.collect(
                DataCapability.FIXTURES,
                source_params={
                    "api_football": {
                        "date": parameters["date"],
                        "timezone": "America/Sao_Paulo",
                    },
                    "openligadb": {
                        "league": parameters["league"],
                        "season": parameters["season"],
                    },
                    "football_data_uk": {
                        "path": parameters["path"],
                    },
                    "thesportsdb": {
                        "date": parameters["date"],
                    },
                    "sportmonks": {
                        "date": parameters["date"],
                    },
                },
            )
            failures.update(report.failed_sources)
            for observation in report.observations:
                payload = RawProviderPayload(
                    provider=observation.provider,
                    resource=observation.capability.value,
                    external_id=observation.external_id,
                    payload=observation.values,
                    collected_at=observation.observed_at,
                )
                if self.raw_store.save(payload):
                    saved += 1
                else:
                    skipped += 1

            odds_report = engine.collect(
                DataCapability.ODDS,
                source_params={
                    "api_football": {
                        "date": parameters["date"],
                    },
                    "the_odds_api": {
                        "sport_keys": tuple(
                            key.strip()
                            for key in self.environment.get(
                                "THE_ODDS_API_SPORT_KEYS",
                                "soccer_brazil_campeonato,"
                                "soccer_epl,soccer_uefa_champs_league",
                            ).split(",")
                            if key.strip()
                        ),
                        "regions": self.environment.get(
                            "THE_ODDS_API_REGIONS", "eu"
                        ),
                        "markets": self.environment.get(
                            "THE_ODDS_API_MARKETS", "h2h,totals"
                        ),
                    },
                },
            )
            failures.update(odds_report.failed_sources)
            for observation in odds_report.observations:
                payload = RawProviderPayload(
                    provider=observation.provider,
                    resource=observation.capability.value,
                    external_id=observation.external_id,
                    payload=observation.values,
                    collected_at=observation.observed_at,
                )
                if self.raw_store.save(payload):
                    saved += 1
                else:
                    skipped += 1

            if self.environment.get("FOOTBALL_DATA_API_TOKEN", "").strip():
                football_provider = self.football_factory()
                health = football_provider.health_check()
                self.health_store.save(health)
                if health.available:
                    data = football_provider.fetch_matches(
                        dateFrom=parameters["date"],
                        dateTo=parameters["date"],
                    )
                    football_data_payload = data
                    payload = RawProviderPayload(
                        "football_data",
                        "matches",
                        parameters["date"],
                        data,
                        datetime.now(timezone.utc),
                    )
                    if self.raw_store.save(payload):
                        saved += 1
                    else:
                        skipped += 1
                else:
                    failures["football_data"] = health.message

            if not report.successful_sources and (
                football_provider is None
                or failures.get("football_data") is not None
            ):
                raise RuntimeError("Nenhum provider real respondeu com sucesso.")

            lineups_saved = self._collect_lineups(
                engine, report.observations
            )
            fusion_observations = (
                report.observations + odds_report.observations
            )
            fusion_result = MatchFusionService(self.session).fuse(
                fusion_observations,
                football_data_payload=football_data_payload,
            )
            operational = OperationalPipelineService(self.session).process(
                fixtures=report.observations,
                odds=odds_report.observations,
            )
            operational["fusion"] = fusion_result
            operational["historical_enrichment"] = (
                HistoricalEnrichmentService(self.session).process(
                    report.observations
                )
            )
            operational["fusion_predictions"] = (
                OperationalPipelineService(
                    self.session
                ).refresh_all_predictions()
            )
            operational["live_snapshots"] = self._persist_live_snapshots(
                report.observations
            )
            operational["lineups"] = lineups_saved
            statistics_saved, settled_bets = self._collect_post_match_statistics(
                engine,
                report.observations,
            )
            operational["statistics"] = statistics_saved
            operational["settled_bets"] = settled_bets
            operational["post_match_predictions"] = (
                OperationalPipelineService(
                    self.session
                ).refresh_all_predictions()
            )
            operational["intelligence"] = (
                OperationalIntelligenceService(
                    self.session
                ).run()
            )
            operational["maturity"] = MaturityService(
                self.session
            ).run()
            operational["stale_matches_reconciled"] = (
                self._reconcile_stale_matches()
            )
            self.session.commit()
            completed = self.monitor.mark_success(
                sync_run.id,
                {
                    "matches": {
                        "created": saved,
                        "updated": 0,
                        "skipped": skipped,
                    }
                },
            )
            return {
                "sync_run_id": completed.id,
                "status": completed.status,
                "duration_seconds": completed.duration_seconds,
                "saved": saved,
                "skipped": skipped,
                "successful_sources": report.successful_sources,
                "failures": failures,
                "degraded": bool(failures),
                "operational": operational,
            }
        except Exception as error:
            self.session.rollback()
            self.monitor.mark_failed(sync_run.id, error)
            raise
        finally:
            engine.close()
            if football_provider is not None:
                football_provider.close()

    def _collect_post_match_statistics(
        self,
        engine: MultiSourceEngine,
        fixtures: tuple[SourceObservation, ...],
    ) -> tuple[int, int]:
        """Coleta somente partidas encerradas ainda sem estatísticas."""
        api_source = next(
            (
                source
                for source in engine.sources
                if source.name == "api_football"
                and DataCapability.STATISTICS
                in getattr(source, "capabilities", ())
            ),
            None,
        )
        cutoff = datetime.now(timezone.utc).replace(
            tzinfo=None
        ) - timedelta(
            days=max(
                1,
                int(self.environment.get(
                    "AUTO_STATS_LOOKBACK_DAYS", "14"
                )),
            )
        )
        matches = self.session.scalars(
            select(Match)
            .outerjoin(
                MatchStatistics,
                MatchStatistics.match_id == Match.id,
            )
            .where(
                Match.status == "finished",
                Match.kickoff_at >= cutoff,
                MatchStatistics.id.is_(None),
            )
            .order_by(Match.kickoff_at.desc())
        ).all()
        fixture_rows = {
            observation.external_id: observation
            for observation in fixtures
            if observation.provider == "api_football"
        }
        retry_cutoff = datetime.now(timezone.utc) - timedelta(
            hours=max(
                1,
                int(self.environment.get(
                    "AUTO_STATS_RETRY_HOURS", "12"
                )),
            )
        )
        candidates = []
        for match in matches:
            fixture_id = self._provider_match_id(
                match, "api_football"
            )
            if not fixture_id or api_source is None:
                continue
            attempted = self.session.scalar(
                select(exists().where(
                    RawProviderPayloadRecord.provider
                    == "api_football",
                    RawProviderPayloadRecord.resource
                    == "statistics_attempt",
                    RawProviderPayloadRecord.external_id == fixture_id,
                    RawProviderPayloadRecord.collected_at
                    >= retry_cutoff,
                ))
            )
            if attempted:
                continue
            fixture_observation = fixture_rows.get(fixture_id)
            if fixture_observation is None:
                raw = self.session.scalar(
                    select(RawProviderPayloadRecord)
                    .where(
                        RawProviderPayloadRecord.provider
                        == "api_football",
                        RawProviderPayloadRecord.resource == "fixtures",
                        RawProviderPayloadRecord.external_id
                        == fixture_id,
                    )
                    .order_by(
                        RawProviderPayloadRecord.collected_at.desc()
                    )
                )
                if raw is None:
                    continue
                fixture_observation = SourceObservation(
                    "api_football",
                    DataCapability.FIXTURES,
                    fixture_id,
                    raw.payload,
                    raw.collected_at,
                )
            has_pending_bet = self.session.scalar(
                select(exists().where(
                    Bet.match_id == match.id,
                    Bet.status == "pending",
                ))
            )
            candidates.append(
                (
                    not bool(has_pending_bet),
                    match,
                    fixture_id,
                    fixture_observation,
                )
            )

        candidates.sort(
            key=lambda item: (
                item[0],
                -item[1].kickoff_at.timestamp(),
            )
        )
        limit = max(
            0,
            int(self.environment.get("AUTO_STATS_MAX_PER_SYNC", "5")),
        )
        pipeline = OperationalPipelineService(self.session)
        stored = settled = 0
        for _, _, fixture_id, fixture_observation in (
            candidates[:limit]
        ):
            try:
                observations = api_source.collect(
                    DataCapability.STATISTICS,
                    fixture=fixture_id,
                )
                attempt_status = (
                    "received" if observations else "empty"
                )
            except Exception as error:
                observations = ()
                attempt_status = (
                    f"failed:{type(error).__name__}"
                )
            attempted_at = datetime.now(timezone.utc)
            self.raw_store.save(
                RawProviderPayload(
                    provider="api_football",
                    resource="statistics_attempt",
                    external_id=fixture_id,
                    payload={
                        "fixture_id": fixture_id,
                        "status": attempt_status,
                        "attempted_at": attempted_at.isoformat(),
                    },
                    collected_at=attempted_at,
                )
            )
            for observation in observations:
                self.raw_store.save(
                    RawProviderPayload(
                        provider=observation.provider,
                        resource=observation.capability.value,
                        external_id=(
                            f"{fixture_id}:{observation.external_id}"
                        ),
                        payload=observation.values,
                        collected_at=observation.observed_at,
                    )
                )
            result = pipeline.process_post_match_statistics(
                fixture_observation,
                observations,
            )
            stored += result["statistics"]
            settled += result["settled_bets"]
        complementary = self._collect_sportmonks_statistics(
            engine, matches
        )
        stored += complementary[0]
        settled += complementary[1]
        return stored, settled

    def _collect_sportmonks_statistics(
        self,
        engine: MultiSourceEngine,
        matches: list[Match],
    ) -> tuple[int, int]:
        source = next(
            (
                item for item in engine.sources
                if item.name == "sportmonks"
                and DataCapability.STATISTICS
                in getattr(item, "capabilities", ())
            ),
            None,
        )
        if source is None:
            return 0, 0
        by_provider_id = {
            provider_id: match
            for match in matches
            if (
                provider_id := self._provider_match_id(
                    match, "sportmonks"
                )
            )
        }
        if not by_provider_id:
            return 0, 0
        dates = sorted(
            {
                match.kickoff_at.date().isoformat()
                for match in by_provider_id.values()
            },
            reverse=True,
        )[:2]
        observations: list[SourceObservation] = []
        for date in dates:
            try:
                observations.extend(
                    source.collect(
                        DataCapability.STATISTICS,
                        date=date,
                    )
                )
            except Exception:
                continue
        stored = settled = 0
        for observation in observations:
            match = by_provider_id.get(observation.external_id)
            if match is None:
                continue
            self.raw_store.save(
                RawProviderPayload(
                    provider=observation.provider,
                    resource=observation.capability.value,
                    external_id=observation.external_id,
                    payload=observation.values,
                    collected_at=observation.observed_at,
                )
            )
            parsed = _sportmonks_match_statistics(
                observation.values, match
            )
            if parsed is None or not match.external_id:
                continue
            result = PostMatchService(self.session).settle_match(
                match_external_id=str(match.external_id),
                source="sportmonks",
                **parsed,
            )
            stored += 1
            settled += len(result["settled_bets"])
        return stored, settled

    def _provider_match_id(
        self,
        match: Match,
        provider: str,
    ) -> str | None:
        if match.source == provider and match.external_id:
            return str(match.external_id)
        decision = self.session.scalar(
            select(IdentityDecisionRecord)
            .where(
                IdentityDecisionRecord.provider == provider,
                IdentityDecisionRecord.candidate_id
                == f"match:{match.id}",
                IdentityDecisionRecord.status == "matched",
            )
            .order_by(
                IdentityDecisionRecord.decided_at.desc()
            )
        )
        if decision is None:
            return None
        prefix = "match:"
        return (
            decision.external_id[len(prefix):]
            if decision.external_id.startswith(prefix)
            else decision.external_id
        )

    def _persist_live_snapshots(
        self,
        fixtures: tuple[SourceObservation, ...],
    ) -> int:
        engine = LiveEngine()
        store = LiveStore(self.session)
        captured = datetime.now(timezone.utc)
        saved = 0
        for observation in fixtures:
            live_values = _provider_live_values(observation)
            if live_values is None:
                continue
            external_id, minute, home_goals, away_goals = live_values
            decision = self.session.scalar(
                select(IdentityDecisionRecord).where(
                    IdentityDecisionRecord.provider
                    == observation.provider,
                    IdentityDecisionRecord.external_id
                    == f"match:{external_id}",
                    IdentityDecisionRecord.status == "matched",
                )
            )
            match_id = (
                decision.candidate_id.removeprefix("match:")
                if decision and decision.candidate_id
                else f"{observation.provider}:{external_id}"
            )
            latest = store.latest(match_id)
            state = (
                LiveMatchState(
                    match_id=match_id,
                    phase=LivePhase(latest.phase),
                    health=LiveHealth(latest.health),
                    minute=latest.minute,
                    home_score=latest.home_score,
                    away_score=latest.away_score,
                    statistics={
                        key: Decimal(str(value))
                        for key, value in latest.statistics.items()
                    },
                    odds={
                        key: Decimal(str(value))
                        for key, value in latest.odds.items()
                    },
                    probabilities={
                        key: Decimal(str(value))
                        for key, value in latest.probabilities.items()
                    },
                    recommendations=tuple(
                        LiveRecommendation(
                            str(item["selection"]),
                            Decimal(str(item["probability"])),
                            Decimal(str(item["odds"])),
                            Decimal(str(item["expected_value"])),
                        )
                        for item in latest.recommendations
                    ),
                    anomalies=tuple(latest.anomalies),
                    push_messages=(),
                    processed_event_ids=tuple(
                        self.session.scalars(
                            select(LiveEventRecord.id).where(
                                LiveEventRecord.match_id == match_id
                            )
                        ).all()
                    ),
                    last_event_at=latest.captured_at,
                    revision=latest.revision,
                )
                if latest else engine.initial(match_id)
            )
            for suffix, kind, payload in (
                (
                    "score",
                    LiveEventType.SCORE,
                    {
                        "home": home_goals,
                        "away": away_goals,
                    },
                ),
                ("clock", LiveEventType.CLOCK, {"minute": minute}),
            ):
                event = LiveEvent(
                    (
                        f"{match_id}:{suffix}:{minute}:"
                        f"{home_goals}:{away_goals}:"
                        f"{observation.provider}"
                    ),
                    match_id,
                    kind,
                    captured,
                    captured,
                    payload,
                )
                store.save_event(event)
                state = engine.ingest(state, event)
            if latest is None or state.revision > latest.revision:
                store.save_snapshot(state, captured)
                saved += 1
        return saved

    def _collect_lineups(
        self,
        engine: MultiSourceEngine,
        fixtures: tuple[SourceObservation, ...],
    ) -> int:
        lineup_sources = [
            source for source in engine.sources
            if DataCapability.LINEUPS
            in getattr(source, "capabilities", ())
        ]
        api_source = next(
            (
                source for source in lineup_sources
                if source.name == "api_football"
            ),
            None,
        )
        now = datetime.now(timezone.utc)
        candidates: list[tuple[datetime, str]] = []
        for observation in fixtures:
            if observation.provider != "api_football":
                continue
            fixture = observation.values.get("fixture", {})
            status = fixture.get("status", {})
            if status.get("short") not in {
                "NS", "TBD", "1H", "HT", "2H", "ET", "BT", "P", "LIVE"
            }:
                continue
            fixture_id = str(fixture.get("id") or "")
            try:
                kickoff = datetime.fromisoformat(
                    str(fixture.get("date")).replace("Z", "+00:00")
                )
            except (TypeError, ValueError):
                continue
            if fixture_id and now - timedelta(hours=1) <= kickoff <= now + timedelta(hours=2):
                already_collected = self.session.scalar(
                    select(
                        exists().where(
                            RawProviderPayloadRecord.provider == "api_football",
                            RawProviderPayloadRecord.resource == "lineups",
                            RawProviderPayloadRecord.external_id.like(
                                f"{fixture_id}:%"
                            ),
                        )
                    )
                )
                if already_collected:
                    continue
                candidates.append((kickoff, fixture_id))
        saved = 0
        limit = max(0, int(self.environment.get("AUTO_LINEUPS_MAX_PER_SYNC", "3")))
        for _, fixture_id in (
            sorted(candidates)[:limit] if api_source else []
        ):
            for observation in api_source.collect(
                DataCapability.LINEUPS, fixture=fixture_id
            ):
                if self.raw_store.save(
                    RawProviderPayload(
                        provider=observation.provider,
                        resource=observation.capability.value,
                        external_id=f"{fixture_id}:{observation.external_id}",
                        payload=observation.values,
                        collected_at=observation.observed_at,
                    )
                ):
                    saved += 1
        for source in lineup_sources:
            if source.name == "api_football":
                continue
            try:
                observations = source.collect(
                    DataCapability.LINEUPS,
                    date=now.date().isoformat(),
                )
            except Exception:
                continue
            for observation in observations:
                payload = observation.values
                if not isinstance(payload, dict) or not payload.get(
                    "lineups"
                ):
                    continue
                if self.raw_store.save(
                    RawProviderPayload(
                        provider=observation.provider,
                        resource=observation.capability.value,
                        external_id=observation.external_id,
                        payload=payload,
                        collected_at=observation.observed_at,
                    )
                ):
                    saved += 1
        return saved

    def _reconcile_stale_matches(self) -> int:
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=4)
        stale = self.session.scalars(
            select(Match).where(
                Match.status == "in_progress",
                Match.kickoff_at < cutoff,
            )
        ).all()
        for match in stale:
            match.status = "finished"
        return len(stale)

    def _fixture_parameters(self) -> dict[str, str]:
        now = datetime.now(ZoneInfo("America/Sao_Paulo"))
        return {
            "date": now.date().isoformat(),
            "league": self.environment.get("OPENLIGADB_LEAGUE", "bl1"),
            "season": self.environment.get("OPENLIGADB_SEASON", str(now.year)),
            "path": self.environment.get(
                "FOOTBALL_DATA_UK_PATH",
                "mmz4281/2526/E0.csv",
            ),
        }


def _provider_live_values(
    observation: SourceObservation,
) -> tuple[str, int, int, int] | None:
    row = observation.values
    if observation.provider == "api_football":
        fixture = row.get("fixture") or {}
        status = fixture.get("status") or {}
        if status.get("short") not in {
            "1H", "HT", "2H", "ET", "BT", "P", "LIVE"
        }:
            return None
        goals = row.get("goals") or {}
        return (
            str(fixture.get("id") or observation.external_id),
            int(status.get("elapsed") or 0),
            int(goals.get("home") or 0),
            int(goals.get("away") or 0),
        )
    if observation.provider == "sportmonks":
        state = row.get("state") or {}
        state_name = str(
            state.get("short_name") or state.get("name") or ""
        ).casefold()
        if not any(
            token in state_name
            for token in ("live", "inplay", "1st", "2nd", "half")
        ):
            return None
        scores = _sportmonks_scores(row)
        return (
            observation.external_id,
            int(row.get("length") or row.get("minute") or 0),
            scores.get("home", 0),
            scores.get("away", 0),
        )
    return None


def _sportmonks_match_statistics(
    row: Mapping[str, object],
    match: Match,
) -> dict[str, object] | None:
    participants = row.get("participants")
    statistics = row.get("statistics")
    if not isinstance(participants, list) or not isinstance(
        statistics, list
    ):
        return None
    locations = {
        str(item.get("id")): str(
            (item.get("meta") or {}).get("location") or ""
        ).casefold()
        for item in participants
        if isinstance(item, dict) and item.get("id") is not None
    }
    values: dict[str, dict[str, object]] = {
        "home": {},
        "away": {},
    }
    for item in statistics:
        if not isinstance(item, dict):
            continue
        location = locations.get(str(item.get("participant_id")))
        if location not in values:
            continue
        stat_type = item.get("type") or {}
        if not isinstance(stat_type, dict):
            continue
        name = str(
            stat_type.get("developer_name")
            or stat_type.get("name")
            or ""
        ).casefold().replace(" ", "_")
        data = item.get("data")
        value = (
            data.get("value")
            if isinstance(data, dict)
            else item.get("value")
        )
        if name and value is not None:
            values[location][name] = value
    if not values["home"] and not values["away"]:
        return None
    scores = _sportmonks_scores(row)
    home_score = (
        int(match.home_score)
        if match.home_score is not None
        else scores.get("home")
    )
    away_score = (
        int(match.away_score)
        if match.away_score is not None
        else scores.get("away")
    )
    if home_score is None or away_score is None:
        return None

    def stat(
        location: str,
        *names: str,
        percentage: bool = False,
    ) -> int | float | None:
        for name in names:
            value = values[location].get(name)
            if value is None:
                continue
            try:
                number = float(str(value).rstrip("%"))
                return number if percentage else int(number)
            except (TypeError, ValueError):
                continue
        return None

    return {
        "home_score": home_score,
        "away_score": away_score,
        "corners_home": stat("home", "corners", "corner_kicks"),
        "corners_away": stat("away", "corners", "corner_kicks"),
        "yellow_cards_home": stat("home", "yellowcards", "yellow_cards"),
        "yellow_cards_away": stat("away", "yellowcards", "yellow_cards"),
        "red_cards_home": stat("home", "redcards", "red_cards"),
        "red_cards_away": stat("away", "redcards", "red_cards"),
        "shots_home": stat("home", "shots_total", "total_shots"),
        "shots_away": stat("away", "shots_total", "total_shots"),
        "shots_on_target_home": stat(
            "home", "shots_on_target", "shots_ongoal"
        ),
        "shots_on_target_away": stat(
            "away", "shots_on_target", "shots_ongoal"
        ),
        "offsides_home": stat("home", "offsides"),
        "offsides_away": stat("away", "offsides"),
        "possession_home": stat(
            "home", "ball_possession", "possessiontime",
            percentage=True,
        ),
        "possession_away": stat(
            "away", "ball_possession", "possessiontime",
            percentage=True,
        ),
        "xg_home": stat(
            "home", "expected_goals", "xg", percentage=True
        ),
        "xg_away": stat(
            "away", "expected_goals", "xg", percentage=True
        ),
    }


def _sportmonks_scores(
    row: Mapping[str, object],
) -> dict[str, int]:
    participants = row.get("participants")
    scores = row.get("scores")
    if not isinstance(participants, list) or not isinstance(scores, list):
        return {}
    locations = {
        str(item.get("id")): str(
            (item.get("meta") or {}).get("location") or ""
        ).casefold()
        for item in participants
        if isinstance(item, dict)
    }
    result: dict[str, int] = {}
    for item in scores:
        if not isinstance(item, dict):
            continue
        location = locations.get(str(item.get("participant_id")))
        score = item.get("score") or {}
        goals = score.get("goals") if isinstance(score, dict) else None
        if location in {"home", "away"} and goals is not None:
            try:
                result[location] = max(
                    result.get(location, 0), int(goals)
                )
            except (TypeError, ValueError):
                continue
    return result
