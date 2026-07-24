from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import SyncRun
from app.services.multi_provider_sync_service import MultiProviderSyncService
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    ProviderHealthRecord,
    RawProviderPayloadRecord,
)
from ultrastats_ai.infrastructure.providers import (
    CollectionReport,
    DataCapability,
    ProviderHealth,
    SourceObservation,
)


NOW = datetime.now(timezone.utc)


class FakeSource:
    def __init__(self, name="api_football", available=True):
        self.name = name
        self.available = available
        self.closed = False

    def health_check(self):
        return ProviderHealth(self.name, self.available, 1, "ok", NOW)

    def close(self):
        self.closed = True


class FakeEngine:
    def __init__(self, *, successful=True):
        self.sources = (FakeSource(),)
        self.successful = successful
        self.closed = False

    def collect(self, capability, **params):
        assert "source_params" in params
        if capability is DataCapability.ODDS:
            return CollectionReport(
                capability,
                (),
                ("api_football",),
                {},
                False,
            )
        assert capability is DataCapability.FIXTURES
        configured = params["source_params"]
        assert configured["api_football"]["timezone"] == "America/Sao_Paulo"
        assert configured["openligadb"]["league"] == "bl1"
        assert configured["football_data_uk"]["path"].endswith(".csv")
        observations = (
            SourceObservation(
                "api_football",
                capability,
                "42",
                {"fixture": {"id": 42}},
                NOW,
            ),
        ) if self.successful else ()
        return CollectionReport(
            capability,
            observations,
            ("api_football",) if self.successful else (),
            {} if self.successful else {"api_football": "offline"},
            not self.successful,
        )

    def close(self):
        self.closed = True
        for source in self.sources:
            source.close()


class FakeFootball:
    def __init__(self, available=True):
        self.available = available
        self.closed = False

    def health_check(self):
        return ProviderHealth("football_data", self.available, 2, "ok", NOW)

    def fetch_matches(self, **filters):
        return {"matches": [], "filters": filters}

    def close(self):
        self.closed = True


def database_session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    CanonicalBase.metadata.create_all(engine)
    return Session(engine)


def test_real_sync_persists_health_payloads_and_is_idempotent():
    session = database_session()
    engine = FakeEngine()
    football = FakeFootball()
    environment = {
        "FOOTBALL_DATA_API_TOKEN": "token",
        "OPENLIGADB_LEAGUE": "bl1",
        "OPENLIGADB_SEASON": "2025",
        "FOOTBALL_DATA_UK_PATH": "season.csv",
    }
    service = MultiProviderSyncService(
        session,
        environment=environment,
        engine_factory=lambda _: engine,
        football_factory=lambda: football,
    )
    first = service.run()
    assert first["status"] == "success"
    assert first["duration_seconds"] is not None
    assert first["saved"] == 2
    assert not first["degraded"]
    assert len(session.scalars(select(RawProviderPayloadRecord)).all()) == 2
    assert len(session.scalars(select(ProviderHealthRecord)).all()) == 2
    assert session.scalar(select(SyncRun)).status == "success"
    assert engine.closed and football.closed

    second_engine = FakeEngine()
    second_football = FakeFootball()
    service = MultiProviderSyncService(
        session,
        environment=environment,
        engine_factory=lambda _: second_engine,
        football_factory=lambda: second_football,
    )
    second = service.run()
    assert second["saved"] == 0
    assert second["skipped"] == 2


def test_real_sync_can_succeed_degraded_without_football_data():
    session = database_session()
    result = MultiProviderSyncService(
        session,
        environment={},
        engine_factory=lambda _: FakeEngine(),
    ).run()
    assert result["status"] == "success"
    assert not result["failures"]


def test_real_sync_records_total_failure():
    session = database_session()
    service = MultiProviderSyncService(
        session,
        environment={},
        engine_factory=lambda _: FakeEngine(successful=False),
    )
    try:
        service.run()
    except RuntimeError as error:
        assert "Nenhum provider" in str(error)
    else:
        raise AssertionError("Falha total deveria bloquear a sincronização.")
    run = session.scalar(select(SyncRun))
    assert run.status == "failed"
