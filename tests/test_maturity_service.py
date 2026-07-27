from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Competition, Market, Match, Odd, Prediction, Team
from app.services.maturity_service import MaturityService
from ultrastats_ai.infrastructure.database.models import CanonicalBase


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
