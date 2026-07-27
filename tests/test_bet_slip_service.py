from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Bankroll, Competition, Market, Match, Odd, Team
from app.services.bet_slip_service import BetSlipService


def test_multiple_slip_reserves_stake_and_combines_odds():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        bankroll = Bankroll(
            name="Principal",
            initial_balance=Decimal("1000"),
            current_balance=Decimal("1000"),
            unit_percentage=1,
        )
        competition = Competition(name="Liga", sport="football")
        teams = [Team(name=f"Time {index}") for index in range(4)]
        market = Market(code="match_winner", name="Resultado", category="result")
        session.add_all((bankroll, competition, market, *teams))
        session.flush()
        matches = [
            Match(
                competition_id=competition.id,
                home_team_id=teams[index * 2].id,
                away_team_id=teams[index * 2 + 1].id,
                kickoff_at=datetime.now() + timedelta(days=1),
                status="scheduled",
                external_id=f"match-{index}",
            )
            for index in range(2)
        ]
        session.add_all(matches)
        session.flush()
        session.add_all(
            Odd(
                match_id=match.id,
                market_id=market.id,
                bookmaker="Book",
                selection="Home",
                odd_value=Decimal("2.00"),
            )
            for match in matches
        )
        session.commit()
        slip = BetSlipService(session).create(
            {
                "bankroll_id": bankroll.id,
                "bookmaker": "Book",
                "stake_amount": 50,
                "legs": [
                    {
                        "match_id": match.id,
                        "market_id": market.id,
                        "selection": "Home",
                    }
                    for match in matches
                ],
            }
        )
        assert slip.kind == "multiple"
        assert slip.total_odds == Decimal("4.0000")
        assert len(slip.legs) == 2
        assert session.get(Bankroll, bankroll.id).current_balance == Decimal("950")
