from app.database.session import SessionLocal
from app.services import TeamService


def test_list_teams() -> None:
    session = SessionLocal()

    try:
        service = TeamService(session)

        teams = service.list_teams()

        assert isinstance(teams, list)
        assert len(teams) >= 1

    finally:
        session.close()