from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Competition, Match, Team
from app.services import MatchService


def test_list_matches() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)

    try:
        competition = Competition(
            name="Premier League", country="England", sport="football"
        )
        home, away = Team(name="Home"), Team(name="Away")
        session.add_all((competition, home, away))
        session.flush()
        session.add(Match(
            competition_id=competition.id,
            home_team_id=home.id,
            away_team_id=away.id,
            kickoff_at=datetime(2026, 7, 30, 12),
            status="scheduled",
        ))
        session.commit()
        service = MatchService(session)

        matches = service.list_matches()

        assert isinstance(matches, list)
        assert len(matches) == 1

    finally:
        session.close()
        engine.dispose()
