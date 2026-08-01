from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Team
from app.services import TeamService


def test_list_teams() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)

    try:
        session.add(Team(name="Team under test"))
        session.commit()
        service = TeamService(session)

        teams = service.list_teams()

        assert isinstance(teams, list)
        assert len(teams) == 1

    finally:
        session.close()
        engine.dispose()
