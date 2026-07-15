from app.repositories import (
    CompetitionRepository,
    MatchRepository,
    TeamRepository,
)
from app.services import MatchService, TeamService


def test_imports() -> None:
    assert TeamRepository is not None
    assert MatchRepository is not None
    assert CompetitionRepository is not None
    assert TeamService is not None
    assert MatchService is not None