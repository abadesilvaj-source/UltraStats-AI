from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import (
    Bankroll,
    Competition,
    Market,
    Match,
    Odd,
    Prediction,
    Team,
)
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
        canceled = BetSlipService(session).cancel(slip.id)
        assert canceled.status == "canceled"
        assert canceled.payout_amount == Decimal("50.00")
        assert all(leg.status == "canceled" for leg in canceled.legs)
        assert session.get(
            Bankroll, bankroll.id
        ).current_balance == Decimal("1000.00")
        with pytest.raises(ValueError, match="Somente bilhetes pendentes"):
            BetSlipService(session).cancel(slip.id)


def test_manual_odds_override_collected_odds_in_analysis_and_slip():
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
        home, away = Team(name="Casa"), Team(name="Fora")
        market = Market(
            code="match_winner", name="Resultado", category="result"
        )
        session.add_all((bankroll, competition, home, away, market))
        session.flush()
        match = Match(
            competition_id=competition.id,
            home_team_id=home.id,
            away_team_id=away.id,
            kickoff_at=datetime.now() + timedelta(days=1),
            status="scheduled",
            external_id="manual-odd-1",
        )
        session.add(match)
        session.flush()
        session.add_all((
            Odd(
                match_id=match.id,
                market_id=market.id,
                bookmaker="Referência",
                selection="Home",
                odd_value=Decimal("2.00"),
            ),
            Prediction(
                match_id=match.id,
                market_id=market.id,
                selection="Home",
                model_version="v1",
                probability=.6,
            ),
        ))
        session.commit()
        payload = {
            "bankroll_id": bankroll.id,
            "bookmaker": "Casa escolhida pelo usuário",
            "stake_amount": 20,
            "legs": [{
                "match_id": match.id,
                "market_id": market.id,
                "selection": "Home",
                "odd_value": 2.35,
            }],
        }

        analysis = BetSlipService(session).analyze(payload)
        slip = BetSlipService(session).create(payload)

        assert analysis["combined_odds"] == 2.35
        assert slip.total_odds == Decimal("2.3500")
        assert slip.potential_return == Decimal("47.00")
        assert slip.legs[0].odd_value == Decimal("2.3500")


def test_manual_market_without_local_id_is_named_and_accepted():
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
        home, away = Team(name="Casa"), Team(name="Fora")
        session.add_all((bankroll, competition, home, away))
        session.flush()
        match = Match(
            competition_id=competition.id,
            home_team_id=home.id,
            away_team_id=away.id,
            kickoff_at=datetime.now() + timedelta(days=1),
            status="scheduled",
            external_id="manual-market-1",
        )
        session.add(match)
        session.commit()
        payload = {
            "bankroll_id": bankroll.id,
            "stake_amount": 10,
            "legs": [{
                "match_id": match.id,
                "market_name": "Jogador para marcar a qualquer momento",
                "selection": "Atacante",
                "odd_value": 2.8,
            }],
        }

        analysis = BetSlipService(session).analyze(payload)
        slip = BetSlipService(session).create(payload)

        assert analysis["unavailable_markets"] == [{
            "leg": 1,
            "market": "Jogador para marcar a qualquer momento",
            "selection": "Atacante",
        }]
        assert slip.total_odds == Decimal("2.8000")
        assert session.get(Market, slip.legs[0].market_id).name == (
            "Jogador para marcar a qualquer momento"
        )

        settled = BetSlipService(session).settle_leg_manually(
            slip.id, slip.legs[0].id, "won"
        )

        assert settled.status == "won"
        assert settled.payout_amount == Decimal("28.00")
        assert session.get(
            Bankroll, bankroll.id
        ).current_balance == Decimal("1018.00")
        with pytest.raises(ValueError, match="já foi liquidado"):
            BetSlipService(session).settle_leg_manually(
                slip.id, slip.legs[0].id, "won"
            )


def test_analyzes_correlated_markets_in_same_match():
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
        home, away = Team(name="Casa"), Team(name="Fora")
        result_market = Market(
            code="match_winner", name="Resultado", category="result"
        )
        goals_market = Market(
            code="over_2_5_goals", name="Gols", category="goals"
        )
        session.add_all((
            bankroll, competition, home, away,
            result_market, goals_market,
        ))
        session.flush()
        match = Match(
            competition_id=competition.id,
            home_team_id=home.id,
            away_team_id=away.id,
            kickoff_at=datetime.now() + timedelta(days=1),
            status="scheduled",
            external_id="correlated-1",
        )
        session.add(match)
        session.flush()
        for market, selection, probability in (
            (result_market, "Home", .75),
            (goals_market, "Over 2.5", .70),
        ):
            session.add_all((
                Odd(
                    match_id=match.id,
                    market_id=market.id,
                    bookmaker="Book",
                    selection=selection,
                    odd_value=Decimal("2"),
                ),
                Prediction(
                    match_id=match.id,
                    market_id=market.id,
                    selection=selection,
                    model_version="v1",
                    probability=probability,
                ),
            ))
        session.flush()
        payload = {
            "bankroll_id": bankroll.id,
            "stake_amount": 10,
            "legs": [
                {
                    "match_id": match.id,
                    "market_id": result_market.id,
                    "selection": "Home",
                },
                {
                    "match_id": match.id,
                    "market_id": goals_market.id,
                    "selection": "Over 2.5",
                },
            ],
        }

        analysis = BetSlipService(session).analyze(payload)
        slip = BetSlipService(session).create(payload)

        assert analysis["correlated_pairs"] == 1
        assert "correlated_legs" in analysis["warnings"]
        assert slip.kind == "multiple"
