from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import (
    Bankroll, Competition, Market, Match, MatchStatistics, Odd,
    Prediction, Team,
)
from api.queries import ApiQueries


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
            kickoff_at=datetime.now(timezone.utc) + timedelta(hours=2),
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


def test_recommendations_always_select_one_model_pick_per_match():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        competition = Competition(
            name="Liga", country="Brasil", season="2026", sport="football"
        )
        home = Team(name="Casa", source="multi_provider")
        away = Team(name="Fora", source="multi_provider")
        session.add_all((competition, home, away))
        session.flush()
        match = Match(
            competition_id=competition.id,
            home_team_id=home.id,
            away_team_id=away.id,
            kickoff_at=datetime.now(timezone.utc) + timedelta(hours=2),
            status="scheduled",
            external_id="consensus-1",
        )
        winner = Market(
            code="match_winner", name="Resultado", category="result"
        )
        goals = Market(
            code="over_2_5_goals", name="Mais de 2.5", category="goals"
        )
        session.add_all((match, winner, goals))
        session.flush()
        session.add_all((
            Prediction(
                match_id=match.id,
                market_id=winner.id,
                selection="Home",
                model_version="v1",
                probability=.54,
                confidence=.52,
                evidence_level="low",
            ),
            Prediction(
                match_id=match.id,
                market_id=goals.id,
                selection="Over 2.5",
                model_version="v1",
                probability=.62,
                confidence=.61,
                evidence_level="medium",
            ),
        ))
        session.commit()

        rows = ApiQueries(
            session, "America/Sao_Paulo"
        ).recommendations()

        primary = [
            row for row in rows
            if row["is_primary_recommendation"]
        ]
        assert len(primary) == 1
        assert primary[0]["selection"] == "Over 2.5"
        assert primary[0]["display_selection"] == "Over 2.5"
        assert primary[0]["recommendation_type"] == "model_pick"
        assert not primary[0]["no_bet"]
        assert sum(not row["no_bet"] for row in rows) == 1
        compact = ApiQueries(
            session, "America/Sao_Paulo"
        ).recommendations(primary_only=True, limit=1)
        assert len(compact) == 1
        assert compact[0]["is_primary_recommendation"]
        assert len(ApiQueries(
            session, "America/Sao_Paulo"
        ).predictions(limit=1)) == 1


def test_stale_live_match_is_exposed_as_finished_with_statistics():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        competition = Competition(
            name="Liga", country="Brasil", season="2026", sport="football"
        )
        home = Team(name="Casa", source="multi_provider")
        away = Team(name="Fora", source="multi_provider")
        session.add_all((competition, home, away))
        session.flush()
        match = Match(
            competition_id=competition.id,
            home_team_id=home.id,
            away_team_id=away.id,
            kickoff_at=datetime.now(timezone.utc) - timedelta(hours=3, minutes=1),
            status="in_progress",
            external_id="stale-live-1",
            home_score=2,
            away_score=1,
        )
        session.add(match)
        session.flush()
        session.add(MatchStatistics(
            match_id=match.id,
            corners_home=7,
            corners_away=3,
            shots_home=12,
            shots_away=8,
        ))
        session.commit()
        queries = ApiQueries(session, "America/Sao_Paulo")

        rows = queries.matches(
            statuses=("scheduled", "in_progress", "finished")
        )
        stored = session.scalar(
            select(MatchStatistics).where(
                MatchStatistics.match_id == match.id
            )
        )

        assert rows[0]["status"] == "finished"
        assert stored.corners_home == 7
        assert stored.shots_away == 8
