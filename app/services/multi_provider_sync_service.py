from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
import os

from sqlalchemy.orm import Session

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
from app.services.operational_pipeline_service import OperationalPipelineService


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
                    }
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

            operational = OperationalPipelineService(self.session).process(
                fixtures=report.observations,
                odds=odds_report.observations,
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

    def _fixture_parameters(self) -> dict[str, str]:
        now = datetime.now(timezone.utc)
        return {
            "date": now.date().isoformat(),
            "league": self.environment.get("OPENLIGADB_LEAGUE", "bl1"),
            "season": self.environment.get("OPENLIGADB_SEASON", str(now.year)),
            "path": self.environment.get(
                "FOOTBALL_DATA_UK_PATH",
                "mmz4281/2526/E0.csv",
            ),
        }
