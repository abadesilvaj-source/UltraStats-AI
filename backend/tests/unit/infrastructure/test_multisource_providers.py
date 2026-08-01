from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import httpx
import pytest

from ultrastats_ai.infrastructure.providers import (
    ApiFootballSource,
    DataCapability,
    FootballDataUKSource,
    GoalApiSource,
    MultiSourceEngine,
    OddsSnapshot,
    OpenLigaDBSource,
    ProviderConfigurationError,
    ProviderResponseError,
    SourceConfig,
    SportmonksSource,
    StatsBombOpenDataSource,
    TheOddsApiSource,
    TheSportsDBSource,
    ZafronixSource,
    build_multi_source_engine,
)


def transport(handler):
    return httpx.MockTransport(handler)


def config(name="source", key=None):
    return SourceConfig(name, "https://source.test", key)


@pytest.mark.parametrize(
    "values",
    [
        ("", "https://x", 1),
        ("x", "", 1),
        ("x", "https://x", 0),
    ],
)
def test_source_config_rejects_invalid_values(values) -> None:
    with pytest.raises(ProviderConfigurationError):
        SourceConfig(values[0], values[1], timeout_seconds=values[2])


def test_api_football_collects_all_contracts_and_health() -> None:
    def handler(request):
        assert request.headers["x-apisports-key"] == "secret"
        if request.url.path == "/status":
            return httpx.Response(200, json={"response": {}})
        return httpx.Response(
            200,
            headers={
                "x-ratelimit-requests-limit": "75000",
                "x-ratelimit-requests-remaining": "74999",
            },
            json={
                "response": [
                    {"fixture": {"id": 42}, "value": request.url.path},
                    "ignored",
                ]
            },
        )

    source = ApiFootballSource(config(key="secret"), transport=transport(handler))
    assert source.health_check().available
    for capability in source.capabilities:
        rows = source.collect(capability, fixture=42)
        assert len(rows) == 1 and rows[0].external_id == "42"
    assert source.last_rate_limit["x-ratelimit-requests-limit"] == 75000
    assert source.last_rate_limit["x-ratelimit-requests-remaining"] == 74999
    with pytest.raises(ValueError):
        source.collect(DataCapability.XG)
    source.close()


def test_api_football_requires_key() -> None:
    with pytest.raises(ProviderConfigurationError):
        ApiFootballSource(config())


def test_goal_api_normalizes_fixture_contract() -> None:
    def handler(request):
        assert request.headers["authorization"] == "Bearer secret"
        return httpx.Response(200, json={"success": True, "data": [{
            "id": "g-1", "matchDate": "2026-07-28",
            "matchTime": "20:00:00", "matchStatus": "SCHEDULED",
            "leagueId": 39, "leagueName": "Premier League",
            "countryName": "England", "leagueYear": 2026,
            "homeTeamId": 1, "homeTeamName": "Home",
            "awayTeamId": 2, "awayTeamName": "Away",
            "homeTeamScore": None, "awayTeamScore": None,
            "matchStadium": "Arena",
        }]})

    source = GoalApiSource(
        config(key="secret"), transport=transport(handler)
    )
    row = source.collect(DataCapability.FIXTURES, limit=1)[0]
    assert row.provider == "goal_api"
    assert row.values["league"]["name"] == "Premier League"
    assert row.values["teams"]["home"]["name"] == "Home"
    source.close()


def test_zafronix_preserves_embedded_match_intelligence() -> None:
    def handler(request):
        return httpx.Response(200, json={"year": 2026, "data": [{
            "id": "wc-1", "kickoffUtc": "2026-07-28T20:00:00Z",
            "status": "final", "homeTeam": {"code": "BRA", "name": "Brazil"},
            "awayTeam": {"code": "ARG", "name": "Argentina"},
            "homeScore": 2, "awayScore": 1, "stadium": "Arena",
            "statistics": {"possession": [55, 45]},
            "lineups": {"home": []}, "weather": {"temperature": 22},
        }]})

    source = ZafronixSource(
        config(key="secret"), transport=transport(handler)
    )
    row = source.collect(DataCapability.FIXTURES, year=2026)[0]
    assert row.provider == "zafronix"
    assert row.values["fixture"]["status"]["short"] == "FT"
    assert row.values["statistics"]["possession"] == [55, 45]
    assert row.values["weather"]["temperature"] == 22
    source.close()


def test_json_source_reports_http_network_json_and_health_failures() -> None:
    cases = (
        lambda _: httpx.Response(503),
        lambda _: httpx.Response(200, text="not-json"),
    )
    for handler in cases:
        source = OpenLigaDBSource(config(), transport=transport(handler))
        health = source.health_check()
        assert not health.available
        source.close()

    def network(request):
        raise httpx.ConnectError("offline", request=request)

    source = OpenLigaDBSource(config(), transport=transport(network))
    with pytest.raises(ProviderResponseError):
        source.collect(DataCapability.FIXTURES, league="bl1", season="2026")
    source.close()


def test_openligadb_normalizes_list_and_rejects_capability() -> None:
    def handler(request):
        payload = [{"matchID": 7}, {"name": "fallback"}, "ignored"]
        return httpx.Response(200, json=payload)

    source = OpenLigaDBSource(config(), transport=transport(handler))
    rows = source.collect(DataCapability.FIXTURES, league="bl1", season=2026)
    assert [row.external_id for row in rows] == ["7", "1"]
    with pytest.raises(ValueError):
        source.collect(DataCapability.ODDS)
    source.close()


def test_engine_supports_parameters_per_source() -> None:
    seen = {}

    class Source:
        capabilities = frozenset({DataCapability.FIXTURES})

        def __init__(self, name):
            self.name = name

        def collect(self, capability, **params):
            seen[self.name] = params
            return ()

        def health_check(self):
            raise AssertionError

        def close(self):
            pass

    engine = MultiSourceEngine(
        (Source("one"), Source("two")),
        {"one": 0, "two": 1},
    )
    report = engine.collect(
        DataCapability.FIXTURES,
        common="value",
        source_params={
            "one": {"specific": 1},
            "two": {"specific": 2},
        },
    )
    assert report.successful_sources == ("one", "two")
    assert seen == {
        "one": {"common": "value", "specific": 1},
        "two": {"common": "value", "specific": 2},
    }


def test_statsbomb_extracts_events_and_xg() -> None:
    payload = [
        {
            "id": "shot-1",
            "minute": 10,
            "team": {"id": 1},
            "player": {"id": 2},
            "shot": {"statsbomb_xg": 0.4, "outcome": {"name": "Goal"}},
        },
        {"id": "pass-1", "type": {"name": "Pass"}},
        "ignored",
    ]
    source = StatsBombOpenDataSource(
        config(), transport=transport(lambda _: httpx.Response(200, json=payload))
    )
    assert source.health_check().available
    assert len(source.collect(DataCapability.EVENTS, match_id=9)) == 2
    xg = source.collect(DataCapability.XG, match_id=9)
    assert len(xg) == 1 and xg[0].values["xg"] == 0.4
    with pytest.raises(ValueError):
        source.collect(DataCapability.ODDS, match_id=9)
    source.close()


def test_football_data_uk_parses_csv_health_and_errors() -> None:
    csv_data = "\ufeffDate,HomeTeam,AwayTeam,B365H\n01/01/26,A,B,2.10\n"

    def handler(request):
        return httpx.Response(200, text=csv_data)

    source = FootballDataUKSource(config(), transport=transport(handler))
    assert source.health_check().available
    rows = source.collect(DataCapability.HISTORICAL_ODDS, path="/data.csv")
    assert rows[0].external_id == "01/01/26|A|B"
    with pytest.raises(ValueError):
        source.collect(DataCapability.XG, path="x")
    source.close()

    failed = FootballDataUKSource(
        config(), transport=transport(lambda _: httpx.Response(404))
    )
    assert not failed.health_check().available
    with pytest.raises(ProviderResponseError):
        failed.collect(DataCapability.FIXTURES, path="missing")
    failed.close()

    def network(request):
        raise httpx.ConnectError("offline", request=request)

    offline = FootballDataUKSource(config(), transport=transport(network))
    with pytest.raises(ProviderResponseError):
        offline.collect(DataCapability.FIXTURES, path="x")
    offline.close()

    empty = FootballDataUKSource(
        config(), transport=transport(lambda _: httpx.Response(200, text="Date\n\n"))
    )
    assert empty.collect(DataCapability.FIXTURES, path="empty.csv") == ()
    empty.close()


def test_thesportsdb_collects_daily_soccer_events() -> None:
    def handler(request):
        if request.url.path.endswith("/all_sports.php"):
            return httpx.Response(200, json={"sports": []})
        assert request.url.params["d"] == "2026-07-27"
        return httpx.Response(
            200,
            json={"events": [{"idEvent": "55"}, "ignored"]},
        )

    source = TheSportsDBSource(config(), transport=transport(handler))
    assert source.health_check().available
    rows = source.collect(DataCapability.FIXTURES, date="2026-07-27")
    assert len(rows) == 1 and rows[0].external_id == "55"
    with pytest.raises(ValueError):
        source.collect(DataCapability.ODDS, date="2026-07-27")
    source.close()


def test_sportmonks_uses_token_and_includes_by_capability() -> None:
    def handler(request):
        assert request.url.params["api_token"] == "token"
        if request.url.path.endswith("/leagues"):
            return httpx.Response(200, json={"data": []})
        if request.url.path.endswith("/livescores/inplay"):
            assert "statistics.type" in request.url.params["include"]
            return httpx.Response(200, json={"data": [{"id": 88}]})
        assert "participants" in request.url.params["include"]
        return httpx.Response(200, json={"data": [{"id": 77}]})

    source = SportmonksSource(
        config(key="token"), transport=transport(handler)
    )
    assert source.health_check().available
    rows = source.collect(DataCapability.FIXTURES, date="2026-07-27")
    assert rows[0].external_id == "77"
    live = source.collect(DataCapability.LIVE)
    assert live[0].external_id == "88"
    with pytest.raises(ValueError):
        source.collect(DataCapability.ODDS, date="2026-07-27")
    source.close()
    with pytest.raises(ProviderConfigurationError):
        SportmonksSource(config())


def test_api_football_rejects_http_200_provider_errors() -> None:
    source = ApiFootballSource(
        config(key="token"),
        transport=transport(
            lambda _: httpx.Response(
                200,
                json={
                    "errors": {"requests": "daily quota reached"},
                    "response": [],
                },
            )
        ),
    )

    assert not source.health_check().available
    with pytest.raises(ProviderResponseError):
        source.collect(DataCapability.LIVE)
    source.close()


def test_the_odds_api_collects_configured_sports() -> None:
    def handler(request):
        assert request.url.params["apiKey"] == "odds-key"
        if request.url.path == "/sports":
            return httpx.Response(200, json=[])
        return httpx.Response(200, json=[{"id": request.url.path}])

    source = TheOddsApiSource(
        config(key="odds-key"), transport=transport(handler)
    )
    assert source.health_check().available
    rows = source.collect(
        DataCapability.ODDS,
        sport_keys=("soccer_epl", "soccer_brazil_campeonato"),
    )
    assert len(rows) == 2
    with pytest.raises(ValueError):
        source.collect(DataCapability.FIXTURES)
    source.close()
    with pytest.raises(ProviderConfigurationError):
        TheOddsApiSource(config())


def test_the_odds_api_skips_inactive_sport_keys() -> None:
    def handler(request):
        if "inactive" in request.url.path:
            return httpx.Response(404)
        return httpx.Response(200, json=[{"id": "available-odds"}])

    source = TheOddsApiSource(
        config(key="odds-key"), transport=transport(handler)
    )
    rows = source.collect(
        DataCapability.ODDS,
        sport_keys=("soccer_inactive", "soccer_epl"),
    )

    assert [row.external_id for row in rows] == ["available-odds"]
    source.close()


def test_multisource_engine_aggregates_and_degrades() -> None:
    healthy = OpenLigaDBSource(
        config(), transport=transport(lambda _: httpx.Response(200, json=[{"id": 1}]))
    )
    failing = FootballDataUKSource(
        config(), transport=transport(lambda _: httpx.Response(500))
    )
    engine = MultiSourceEngine(
        (failing, healthy),
        {"openligadb": 1, "football_data_uk": 2},
    )
    report = engine.collect(
        DataCapability.FIXTURES,
        league="bl1",
        season="2026",
        path="x.csv",
    )
    assert report.degraded
    assert report.successful_sources == ("openligadb",)
    assert "football_data_uk" in report.failed_sources
    no_source = engine.collect(DataCapability.XG, match_id=1)
    assert no_source.degraded and not no_source.successful_sources
    engine.close()


def test_odds_snapshot_validates_business_fields() -> None:
    now = datetime.now(timezone.utc)
    snapshot = OddsSnapshot("api", "match", "book", "1x2", "home", Decimal("2"), now)
    assert snapshot.decimal_odds == 2
    with pytest.raises(ValueError):
        OddsSnapshot("", "match", "book", "1x2", "home", Decimal("1"), now)


def test_factory_enables_paid_source_only_with_key(monkeypatch) -> None:
    responses = {
        name: transport(lambda _: httpx.Response(200, json=[]))
        for name in (
            "api_football",
            "openligadb",
            "football_data_uk",
            "statsbomb_open_data",
            "thesportsdb",
            "sportmonks",
            "the_odds_api",
        )
    }
    without_key = build_multi_source_engine({}, transports=responses)
    assert {source.name for source in without_key.sources} == {
        "openligadb",
        "football_data_uk",
        "statsbomb_open_data",
        "thesportsdb",
    }
    without_key.close()
    with_key = build_multi_source_engine(
        {
            "API_FOOTBALL_KEY": "key",
            "SPORTMONKS_API_TOKEN": "token",
            "THE_ODDS_API_KEY": "odds",
            "PROVIDER_PRIORITY": "openligadb,api_football",
        },
        transports=responses,
    )
    assert {source.name for source in with_key.sources} == {
        "api_football",
        "openligadb",
        "football_data_uk",
        "statsbomb_open_data",
        "thesportsdb",
        "sportmonks",
        "the_odds_api",
    }
    with_key.close()
    monkeypatch.setenv("API_FOOTBALL_KEY", "")
    environment_engine = build_multi_source_engine(transports=responses)
    assert len(environment_engine.sources) == 4
    environment_engine.close()
