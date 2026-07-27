from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Bankroll, Competition, Market, Match, Odd, Prediction, Team
from backend.queries import ApiQueries


def test_api_returns_only_active_matches_in_user_timezone():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        competition = Competition(
            name="Liga", country="Brasil", season="2026", sport="football"
        )
        home = Team(name="Casa", source="api_football")
        away = Team(name="Fora", source="api_football")
        session.add_all((competition, home, away))
        session.flush()
        match = Match(
            competition_id=competition.id,
            home_team_id=home.id,
            away_team_id=away.id,
            kickoff_at=datetime(2026, 7, 26, 20, tzinfo=timezone.utc),
            status="scheduled",
            external_id="api-1",
        )
        market = Market(code="match_winner", name="Resultado", category="result")
        bankroll = Bankroll(
            name="Principal",
            currency="BRL",
            initial_balance=Decimal("1000"),
            current_balance=Decimal("1000"),
            unit_percentage=1,
        )
        session.add_all((match, market, bankroll))
        session.flush()
        session.add(
            Prediction(
                match_id=match.id,
                market_id=market.id,
                selection="Home",
                model_version="v1",
                probability=.6,
                expected_value=.1,
            )
        )
        session.commit()
        queries = ApiQueries(session, "America/Sao_Paulo")
        result = queries.matches()
        assert len(result) == 1
        assert result[0]["kickoff_at"].endswith("-03:00")
        assert queries.recommendations()[0]["match"] == "Casa x Fora"
