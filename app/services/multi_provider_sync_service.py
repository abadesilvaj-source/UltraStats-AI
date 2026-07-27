from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
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
    build_football_data_provider,
    build_multi_source_engine,
)
from ultrastats_ai.infrastructure.providers.persistence import (
    SqlAlchemyHealthStore,
    SqlAlchemyRawPayloadStore,
)
from ultrastats_ai.infrastructure.database.models import (
    RawProviderPayloadRecord,
)
from app.services.operational_pipeline_service import OperationalPipelineService
from app.services.match_fusion_service import MatchFusionService
from app.services.historical_enrichment_service import HistoricalEnrichmentService
from ultrastats_ai.domain.live import LiveEngine, LiveEvent, LiveEventType
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
            operational = OperationalPipelineService(self.session).process(
                fixtures=report.observations,
                odds=odds_report.observations,
            )
            operational["fusion"] = MatchFusionService(self.session).fuse(
                report.observations,
                football_data_payload=football_data_payload,
            )
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
        if api_source is None:
            return 0, 0

        candidates = []
        for observation in fixtures:
            if observation.provider != "api_football":
                continue
            fixture = observation.values.get("fixture", {})
            status = fixture.get("status", {})
            external_id = str(fixture.get("id", "")).strip()
            if status.get("short") not in {"FT", "AET", "PEN"} or not external_id:
                continue
            match = self.session.scalar(
                select(Match).where(Match.external_id == external_id)
            )
            if match is None:
                continue
            already_stored = self.session.scalar(
                select(
                    exists().where(MatchStatistics.match_id == match.id)
                )
            )
            if already_stored:
                continue
            has_pending_bet = self.session.scalar(
                select(
                    exists().where(
                        Bet.match_id == match.id,
                        Bet.status == "pending",
                    )
                )
            )
            candidates.append((not bool(has_pending_bet), observation))

        candidates.sort(key=lambda item: item[0])
        limit = max(
            0,
            int(self.environment.get("AUTO_STATS_MAX_PER_SYNC", "1")),
        )
        pipeline = OperationalPipelineService(self.session)
        stored = settled = 0
        for _, fixture_observation in candidates[:limit]:
            fixture_id = str(
                fixture_observation.values["fixture"]["id"]
            )
            observations = api_source.collect(
                DataCapability.STATISTICS,
                fixture=fixture_id,
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
        return stored, settled

    def _persist_live_snapshots(
        self,
        fixtures: tuple[SourceObservation, ...],
    ) -> int:
        engine = LiveEngine()
        store = LiveStore(self.session)
        captured = datetime.now(timezone.utc)
        saved = 0
        for observation in fixtures:
            if observation.provider != "api_football":
                continue
            row = observation.values
            fixture = row.get("fixture", {})
            status = fixture.get("status", {})
            if status.get("short") not in {
                "1H", "HT", "2H", "ET", "BT", "P", "LIVE"
            }:
                continue
            match_id = str(fixture.get("id"))
            state = engine.initial(match_id)
            minute = int(status.get("elapsed") or 0)
            goals = row.get("goals", {})
            for suffix, kind, payload in (
                (
                    "score",
                    LiveEventType.SCORE,
                    {
                        "home": int(goals.get("home") or 0),
                        "away": int(goals.get("away") or 0),
                    },
                ),
                ("clock", LiveEventType.CLOCK, {"minute": minute}),
            ):
                event = LiveEvent(
                    f"{match_id}:{suffix}:{minute}",
                    match_id,
                    kind,
                    captured,
                    captured,
                    payload,
                )
                store.save_event(event)
                state = engine.ingest(state, event)
            store.save_snapshot(state, captured)
            saved += 1
        return saved

    def _collect_lineups(
        self,
        engine: MultiSourceEngine,
        fixtures: tuple[SourceObservation, ...],
    ) -> int:
        api_source = next(
            (
                source for source in engine.sources
                if source.name == "api_football"
                and DataCapability.LINEUPS in getattr(source, "capabilities", ())
            ),
            None,
        )
        if api_source is None:
            return 0
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
        for _, fixture_id in sorted(candidates)[:limit]:
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
        return saved

    def _reconcile_stale_matches(self) -> int:
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=6)
        stale = self.session.scalars(
            select(Match).where(
                Match.status == "in_progress",
                Match.kickoff_at < cutoff,
            )
        ).all()
        for match in stale:
            match.status = "finished" if (
                match.home_score is not None and match.away_score is not None
            ) else "cancelled"
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
