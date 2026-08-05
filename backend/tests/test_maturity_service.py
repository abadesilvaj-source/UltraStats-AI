from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Competition, Market, Match, Odd, Prediction, Team
from app.services.maturity_service import MaturityService
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    ProviderHealthRecord,
    OddsSnapshotRecord,
    RawProviderPayloadRecord,
)


def test_reports_coverage_and_persists_operational_metrics():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    CanonicalBase.metadata.create_all(engine)
    with Session(engine) as session:
        competition = Competition(
            name="Premier League", country="England", sport="football"
        )
        home, away = Team(name="Casa"), Team(name="Fora")
        market = Market(
            code="match_winner", name="Resultado", category="result"
        )
        session.add_all((competition, home, away, market))
        session.flush()
        match = Match(
            competition_id=competition.id,
            home_team_id=home.id,
            away_team_id=away.id,
            kickoff_at=datetime.now(timezone.utc) + timedelta(hours=2),
            status="scheduled",
            source="api_football",
            external_id="quality-1",
        )
        session.add(match)
        session.flush()
        session.add_all((
            Odd(
                match_id=match.id,
                market_id=market.id,
                bookmaker="Book",
                selection="Home",
                odd_value=Decimal("2"),
            ),
            Prediction(
                match_id=match.id,
                market_id=market.id,
                selection="Home",
                model_version="v1",
                probability=.6,
            ),
        ))
        session.flush()

        report = MaturityService(session).run()
        session.commit()

        assert report["matches"]["active"] == 1
        assert report["coverage"]["odds"] == 1
        assert report["coverage"]["predictions"] == 1
        assert report["quality_score"] > 0


def test_provider_availability_follows_sync_cadence_and_recent_payload():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    CanonicalBase.metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        session.add_all((
            ProviderHealthRecord(
                provider="api_football",
                available=True,
                latency_ms=100,
                message="ok",
                checked_at=now - timedelta(hours=7),
            ),
            ProviderHealthRecord(
                provider="football_data",
                available=True,
                latency_ms=100,
                message="ok",
                checked_at=now - timedelta(hours=13),
            ),
            RawProviderPayloadRecord(
                provider="football_data",
                resource="fixtures",
                external_id="recent-evidence",
                fingerprint="recent-evidence-fingerprint",
                payload={"ok": True},
                collected_at=now - timedelta(hours=1),
            ),
            ProviderHealthRecord(
                provider="openligadb",
                available=True,
                latency_ms=100,
                message="ok",
                checked_at=now - timedelta(hours=13),
            ),
        ))
        session.flush()

        providers = MaturityService(session)._provider_status(now)

        assert providers["api_football"]["available"] is True
        assert providers["api_football"]["availability_evidence"] == "health"
        assert providers["football_data"]["available"] is True
        assert providers["football_data"]["availability_evidence"] == "payload"
        assert providers["openligadb"]["available"] is False


def test_empty_eligible_population_is_not_reported_as_full_coverage():
    assert MaturityService._ratio(0, 0) == 0.0
    assert MaturityService._ratio(9, 10) == 0.9


def test_odds_denominator_requires_provider_coverage_evidence():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine); CanonicalBase.metadata.create_all(engine)
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        competition = Competition(name="Premier League", country="England")
        home, away = Team(name="H"), Team(name="A")
        market = Market(code="result", name="Result", category="result")
        session.add_all((competition, home, away, market)); session.flush()
        covered = Match(competition_id=competition.id, home_team_id=home.id,
                        away_team_id=away.id, kickoff_at=now + timedelta(hours=2),
                        status="scheduled", source="api_football", external_id="c1")
        uncovered = Match(competition_id=competition.id, home_team_id=home.id,
                          away_team_id=away.id, kickoff_at=now + timedelta(hours=3),
                          status="scheduled", source="api_football", external_id="c2")
        session.add_all((covered, uncovered)); session.flush()
        session.add_all((
            Odd(match_id=covered.id, market_id=market.id, bookmaker="Book",
                selection="home", odd_value=Decimal("2"), collected_at=now),
            OddsSnapshotRecord(provider="api_football", match_id=str(covered.id),
                bookmaker="Book", market="result", selection="home",
                decimal_odds="2", captured_at=now),
        )); session.flush()
        report = MaturityService(session).report()
        assert report["matches"]["odds_eligible"] == 2
        assert report["matches"]["odds_provider_covered"] == 1
        assert report["coverage"]["odds"] == 1


def test_empty_eligible_population_is_not_reported_as_full_coverage():
    assert MaturityService._ratio(0, 0) == 0.0
    assert MaturityService._ratio(9, 10) == 0.9
