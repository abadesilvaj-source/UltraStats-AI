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
    RawProviderPayloadRecord,
)


def test_reports_coverage_and_persists_operational_metrics():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    CanonicalBase.metadata.create_all(engine)
    with Session(engine) as session:
        competition = Competition(name="Liga", sport="football")
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
