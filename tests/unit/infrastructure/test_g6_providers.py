from datetime import datetime, timezone

import httpx
import pytest

from ultrastats_ai.infrastructure.providers import (
    FootballDataProvider,
    InMemoryRawPayloadStore,
    ProviderCollector,
    ProviderConfig,
    ProviderConfigurationError,
    ProviderDashboard,
    ProviderHTTPClient,
    ProviderResponseError,
    RateLimiter,
    RawProviderPayload,
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
    assert ProviderDashboard().snapshot((provider,))[0].available
    client.close()

    failed = FootballDataProvider(_client(lambda _: httpx.Response(500), retries=0))
    assert not failed.health_check().available
    failed.client.close()
