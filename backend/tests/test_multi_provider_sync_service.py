from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Competition, Match, SyncRun, Team
from app.services.match_fusion_service import MatchFusionService
from app.services.multi_provider_sync_service import (
    MultiProviderSyncService,
    _sportmonks_match_statistics,
)
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
    def __init__(self, *, successful=True, odds_failures=None):
        self.sources = (FakeSource(),)
        self.successful = successful
        self.odds_failures = odds_failures or {}
        self.closed = False

    def collect(self, capability, **params):
        assert "source_params" in params
        if capability is DataCapability.ODDS:
            return CollectionReport(
                capability,
                (),
                ("api_football",),
                self.odds_failures,
                bool(self.odds_failures),
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


class FakeLiveEngine(FakeEngine):
    def collect(self, capability, **params):
        assert capability is DataCapability.LIVE
        assert params["source_params"]["api_football"]["live"] == "all"
        observation = SourceObservation(
            "api_football",
            capability,
            "42",
            {
                "fixture": {
                    "id": 42,
                    "date": "2026-07-27T16:00:00+00:00",
                    "status": {"short": "1H", "elapsed": 20},
                },
                "league": {
                    "id": 10,
                    "name": "Live League",
                    "country": "Brazil",
                },
                "teams": {
                    "home": {"id": 1, "name": "Home"},
                    "away": {"id": 2, "name": "Away"},
                },
                "goals": {"home": 1, "away": 0},
            },
            NOW,
        )
        return CollectionReport(
            capability,
            (observation,),
            ("api_football", "sportmonks"),
            {},
            False,
        )


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


def test_odds_worker_rotates_a_bounded_number_of_competitions():
    session = database_session()
    keys = ("league_a", "league_b", "league_c", "league_d", "league_e")
    service = MultiProviderSyncService(
        session,
        environment={
            "THE_ODDS_API_SPORT_KEYS": ",".join(keys),
            "THE_ODDS_API_KEYS_PER_CYCLE": "2",
            "ODDS_SYNC_INTERVAL_MINUTES": "15",
        },
        engine_factory=lambda _: FakeEngine(),
    )

    selected = service._rotating_odds_sport_keys()

    assert len(selected) == 2
    assert len(set(selected)) == 2
    assert set(selected).issubset(keys)


def test_recent_raw_fixtures_recovers_latest_unique_observation():
    session = database_session()
    session.add_all([
        RawProviderPayloadRecord(
            provider="api_football", resource="fixtures",
            external_id="fixture-1", fingerprint="old",
            payload={"version": "old"},
            collected_at=NOW - timedelta(hours=2),
        ),
        RawProviderPayloadRecord(
            provider="api_football", resource="fixtures",
            external_id="fixture-1", fingerprint="new",
            payload={"version": "new"}, collected_at=NOW,
        ),
        RawProviderPayloadRecord(
            provider="api_football", resource="odds",
            external_id="fixture-1", fingerprint="odds",
            payload={}, collected_at=NOW,
        ),
    ])
    session.commit()

    recovered = MultiProviderSyncService(
        session, environment={}, engine_factory=lambda _: FakeEngine()
    )._recent_raw_fixtures(hours=36)

    assert len(recovered) == 1
    assert recovered[0].external_id == "fixture-1"
    assert recovered[0].values == {"version": "new"}
    recovered_odds = MultiProviderSyncService(
        session, environment={}, engine_factory=lambda _: FakeEngine()
    )._recent_raw_odds(hours=12)
    assert len(recovered_odds) == 1
    assert recovered_odds[0].capability is DataCapability.ODDS


def test_sportmonks_developer_state_is_recognized_as_live():
    db = database_session()
    observation = SourceObservation(
        "sportmonks", DataCapability.LIVE, "live-1",
        {
            "id": "live-1", "starting_at": NOW.isoformat(),
            "state": {"developer_name": "INPLAY_1ST_HALF"},
            "participants": [
                {"id": 1, "name": "Home", "meta": {"location": "home"}},
                {"id": 2, "name": "Away", "meta": {"location": "away"}},
            ],
            "league": {"name": "League"},
        }, NOW,
    )

    adapted = MatchFusionService(db)._adapt(observation)

    assert adapted is not None
    assert adapted.status == "in_progress"


def test_stale_reconciliation_preserves_match_present_in_live_feed():
    db = database_session()
    competition = Competition(name="League", sport="football")
    home, away = Team(name="Home"), Team(name="Away")
    db.add_all((competition, home, away))
    db.flush()
    match = Match(
        competition_id=competition.id,
        home_team_id=home.id,
        away_team_id=away.id,
        kickoff_at=NOW.replace(tzinfo=None) - timedelta(hours=4),
        status="in_progress", source="api_football", external_id="live-1",
    )
    db.add(match)
    db.commit()
    observation = SourceObservation(
        "api_football", DataCapability.LIVE, "live-1", {}, NOW
    )

    changed = MultiProviderSyncService(
        db, environment={}, engine_factory=lambda _: FakeEngine()
    )._reconcile_stale_matches((observation,))

    assert changed == 0
    assert match.status == "in_progress"


def test_partial_provider_failure_is_persisted_as_degraded():
    session = database_session()
    result = MultiProviderSyncService(
        session,
        environment={},
        engine_factory=lambda _: FakeEngine(
            odds_failures={"the_odds_api": "HTTP 429"}
        ),
    ).run()

    run = session.scalar(select(SyncRun))
    assert result["status"] == "degraded"
    assert result["degraded"]
    assert run.status == "degraded"
    assert "the_odds_api" in (run.error_message or "")


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


def test_live_sync_persists_and_promotes_current_score():
    session = database_session()
    result = MultiProviderSyncService(
        session,
        environment={},
        engine_factory=lambda _: FakeLiveEngine(),
    ).run_live()

    assert result["status"] == "success"
    assert result["saved"] == 1
    assert result["successful_sources"] == (
        "api_football", "sportmonks"
    )
    payload = session.scalar(select(RawProviderPayloadRecord))
    assert payload.resource == "live"


def test_normalizes_sportmonks_complementary_statistics():
    row = {
        "participants": [
            {"id": 10, "meta": {"location": "home"}},
            {"id": 20, "meta": {"location": "away"}},
        ],
        "statistics": [
            {
                "participant_id": 10,
                "type": {"developer_name": "CORNERS"},
                "data": {"value": 7},
            },
            {
                "participant_id": 20,
                "type": {"developer_name": "CORNERS"},
                "data": {"value": 4},
            },
            {
                "participant_id": 10,
                "type": {"developer_name": "EXPECTED_GOALS"},
                "data": {"value": 1.8},
            },
        ],
    }

    result = _sportmonks_match_statistics(
        row, SimpleNamespace(home_score=2, away_score=1)
    )

    assert result["home_score"] == 2
    assert result["corners_home"] == 7
    assert result["corners_away"] == 4
    assert result["xg_home"] == 1.8
