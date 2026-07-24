from datetime import datetime, timezone
import importlib.util
from pathlib import Path

import httpx
import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    ProviderHealthRecord,
    RawProviderPayloadRecord,
)

from ultrastats_ai.infrastructure.providers import (
    FootballDataProvider,
    InMemoryRawPayloadStore,
    ProviderCollector,
    ProviderConfig,
    ProviderConfigurationError,
    ProviderDashboard,
    ProviderHTTPClient,
    ProviderHealth,
    ProviderRegistry,
    ProviderResponseError,
    RateLimiter,
    RawProviderPayload,
    SqlAlchemyHealthStore,
    SqlAlchemyRawPayloadStore,
    build_football_data_provider,
)


def test_config_store_and_rate_limiter() -> None:
    config = ProviderConfig(" token ")
    assert config.base_url.endswith("/v4")
    for kwargs in (
        {"api_token": ""},
        {"api_token": "x", "requests_per_minute": 0},
        {"api_token": "x", "timeout_seconds": 0},
        {"api_token": "x", "max_retries": -1},
    ):
        with pytest.raises(ProviderConfigurationError):
            ProviderConfig(**kwargs)
    loaded = ProviderConfig.from_environment(
        {
            "FOOTBALL_DATA_API_TOKEN": "football-token",
            "FOOTBALL_DATA_BASE_URL": "https://example.test/v4",
            "PROVIDER_DEFAULT_REQUESTS_PER_MINUTE": "20",
            "PROVIDER_HTTP_TIMEOUT_SECONDS": "5",
            "PROVIDER_HTTP_MAX_RETRIES": "2",
        }
    )
    assert loaded.api_token == "football-token" and loaded.requests_per_minute == 20
    payload = RawProviderPayload(
        "p", "matches", None, {"id": 1}, datetime.now(timezone.utc)
    )
    store = InMemoryRawPayloadStore()
    assert store.save(payload)
    assert not store.save(payload)
    moments = iter((0.0, 1.0, 6.0, 20.0))
    sleeps: list[float] = []
    limiter = RateLimiter(12, clock=lambda: next(moments), sleeper=sleeps.append)
    limiter.acquire()
    limiter.acquire()
    limiter.acquire()
    assert sleeps == [4.0]


def _client(handler, retries=1, sleeps=None):
    return ProviderHTTPClient(
        ProviderConfig("secret", max_retries=retries),
        transport=httpx.MockTransport(handler),
        sleeper=(sleeps if sleeps is not None else lambda _: None),
    )


def test_http_success_headers_limiter_and_errors() -> None:
    acquired: list[bool] = []

    class Limiter:
        def acquire(self):
            acquired.append(True)

    def success(request):
        assert request.headers["X-Auth-Token"] == "secret"
        return httpx.Response(200, json={"ok": True})

    client = ProviderHTTPClient(
        ProviderConfig("secret"),
        transport=httpx.MockTransport(success),
        limiter=Limiter(),  # type: ignore[arg-type]
    )
    assert client.get_json("/test") == {"ok": True}
    assert acquired == [True]
    client.close()

    invalid = _client(lambda _: httpx.Response(200, content=b"{"))
    with pytest.raises(ProviderResponseError, match="JSON"):
        invalid.get_json("/")
    invalid.close()
    array = _client(lambda _: httpx.Response(200, json=[]))
    with pytest.raises(ProviderResponseError, match="objeto"):
        array.get_json("/")
    array.close()
    denied = _client(lambda _: httpx.Response(401))
    with pytest.raises(ProviderResponseError, match="401"):
        denied.get_json("/")
    denied.close()


def test_http_retries_status_network_and_exhaustion() -> None:
    calls = 0
    sleeps: list[float] = []

    def transient(_):
        nonlocal calls
        calls += 1
        return httpx.Response(429, headers={"Retry-After": "0"}) if calls == 1 else httpx.Response(200, json={"ok": 1})

    client = _client(transient, sleeps=sleeps.append)
    assert client.get_json("/") == {"ok": 1}
    assert sleeps == [0.0]
    client.close()

    calls = 0

    def network(request):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ConnectError("down", request=request)
        return httpx.Response(200, json={"ok": 2})

    client = _client(network, sleeps=sleeps.append)
    assert client.get_json("/") == {"ok": 2}
    client.close()
    failed = _client(lambda request: (_ for _ in ()).throw(httpx.ConnectError("down", request=request)), retries=0)
    with pytest.raises(ProviderResponseError, match="rede"):
        failed.get_json("/")
    failed.close()


def test_football_data_collector_health_and_dashboard(monkeypatch) -> None:
    endpoints: list[tuple[str, object]] = []

    def handler(request):
        endpoints.append((request.url.path, request.url.params))
        return httpx.Response(200, json={"items": []})

    client = _client(handler)
    provider = FootballDataProvider(client)
    assert len(provider.capabilities) == 4
    assert provider.fetch_competitions() == {"items": []}
    assert provider.fetch_teams("PL") == {"items": []}
    assert provider.fetch_matches(status="SCHEDULED") == {"items": []}
    assert provider.fetch_standings("PL") == {"items": []}
    store = InMemoryRawPayloadStore()
    collector = ProviderCollector(provider, store)
    result = collector.collect("teams", competition="PL")
    assert result.external_id == "PL" and store.payloads == [result]
    collector.collect("matches", status="FINISHED")
    collector.collect("competitions")
    collector.collect("standings", competition="PL")
    with pytest.raises(ValueError, match="desconhecido"):
        collector.collect("odds")
    health = provider.health_check()
    assert health.available and health.latency_ms >= 0
    saved = []
    assert ProviderDashboard().snapshot((provider,), saved.append)[0].available
    assert saved[0].available
    provider.close()

    failed = FootballDataProvider(_client(lambda _: httpx.Response(500), retries=0))
    assert not failed.health_check().available
    failed.close()


def test_registry_builder_and_sqlalchemy_stores(monkeypatch) -> None:
    registry = ProviderRegistry()
    factory = lambda: FootballDataProvider(
        _client(lambda _: httpx.Response(200, json={}))
    )
    with pytest.raises(ValueError):
        registry.register("", factory)
    registry.register("Football_Data", factory)
    assert registry.names() == ("football_data",)
    with pytest.raises(ValueError, match="registrado"):
        registry.register("football_data", factory)
    registry.register("football_data", factory, replace=True)
    provider = registry.create("FOOTBALL_DATA")
    provider.close()
    with pytest.raises(LookupError):
        registry.create("missing")

    built = build_football_data_provider(
        ProviderConfig("x"),
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json={})),
    )
    assert built.health_check().available
    built.close()
    monkeypatch.setenv("FOOTBALL_DATA_API_TOKEN", "environment-token")
    environment_built = build_football_data_provider(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json={}))
    )
    assert environment_built.health_check().available
    environment_built.close()

    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            raw_store = SqlAlchemyRawPayloadStore(session)
            payload = RawProviderPayload(
                "football_data",
                "matches",
                "1",
                {"match": {"id": 1}},
                datetime.now(timezone.utc),
            )
            assert raw_store.save(payload)
            session.commit()
            assert not raw_store.save(payload)
            assert session.scalar(select(RawProviderPayloadRecord)) is not None
            health_store = SqlAlchemyHealthStore(session)
            old = ProviderHealth(
                "football_data", False, 10, "old", datetime.now(timezone.utc)
            )
            new = ProviderHealth(
                "football_data", True, 10, "new", datetime.now(timezone.utc)
            )
            health_store.save(old)
            health_store.save(new)
            session.commit()
            latest = health_store.latest()
            assert len(latest) == 1
            assert latest[0].message == new.message and latest[0].available
            assert session.scalar(select(ProviderHealthRecord)) is not None
    finally:
        engine.dispose()


def test_provider_migration_upgrade_and_downgrade() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "migrations"
        / "versions"
        / "8b6a6d20e002_create_provider_operations.py"
    )
    spec = importlib.util.spec_from_file_location("provider_migration", path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    names = {"provider_raw_payloads", "provider_health_checks"}
    try:
        with engine.begin() as connection:
            migration.op = Operations(MigrationContext.configure(connection))
            migration.upgrade()
            assert names <= set(connection.dialect.get_table_names(connection))
            migration.downgrade()
            assert names.isdisjoint(connection.dialect.get_table_names(connection))
    finally:
        engine.dispose()
