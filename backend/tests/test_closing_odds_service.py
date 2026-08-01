from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Competition, Market, Match, Odd, Team
from app.services.closing_odds_service import ClosingOddsService


def test_marks_only_latest_pre_match_price_per_bookmaker_and_selection():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    competition = Competition(name="Premier League", country="England")
    home, away = Team(name="Home"), Team(name="Away")
    market = Market(code="match_winner", name="Resultado", category="result")
    session.add_all((competition, home, away, market))
    session.flush()
    kickoff = datetime(2026, 7, 30, 12)
    match = Match(
        competition_id=competition.id,
        home_team_id=home.id,
        away_team_id=away.id,
        kickoff_at=kickoff,
        status="in_progress",
    )
    session.add(match)
    session.flush()
    session.add_all([
        Odd(match_id=match.id, market_id=market.id, bookmaker="Book",
            selection="Home", odd_value=Decimal("2.00"),
            collected_at=kickoff - timedelta(hours=2)),
        Odd(match_id=match.id, market_id=market.id, bookmaker="Book",
            selection="Home", odd_value=Decimal("2.10"),
            collected_at=kickoff - timedelta(minutes=5)),
        Odd(match_id=match.id, market_id=market.id, bookmaker="Book",
            selection="Home", odd_value=Decimal("2.20"),
            collected_at=kickoff + timedelta(minutes=1)),
    ])
    session.flush()

    assert ClosingOddsService(session).mark(kickoff + timedelta(minutes=2)) == 1
    closing = session.scalar(select(Odd).where(Odd.is_closing.is_(True)))
    assert closing is not None
    assert closing.odd_value == Decimal("2.10")
