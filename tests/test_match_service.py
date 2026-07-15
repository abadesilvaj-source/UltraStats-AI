from app.database.session import SessionLocal
from app.services import MatchService


def test_list_matches() -> None:
    session = SessionLocal()

    try:
        service = MatchService(session)

        matches = service.list_matches()

        assert isinstance(matches, list)
        assert len(matches) >= 1

    finally:
        session.close()