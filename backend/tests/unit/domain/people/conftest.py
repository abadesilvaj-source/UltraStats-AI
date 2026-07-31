"""Fixtures compartilhadas dos testes do People Context."""

import pytest

from ultrastats_ai.domain.people import (
    Coach,
    CoachRole,
    CoachStatus,
    Player,
    PlayerStatus,
    Referee,
    RefereeRole,
    RefereeStatus,
)
from ultrastats_ai.domain.shared import (
    CoachId,
    PersonId,
    PlayerId,
    RefereeId,
)


@pytest.fixture
def person_id() -> PersonId:
    return PersonId.new()


@pytest.fixture
def player(person_id: PersonId) -> Player:
    return Player(
        id=PlayerId.new(),
        person_id=person_id,
        status=PlayerStatus.PROFESSIONAL,
    )


@pytest.fixture
def coach(person_id: PersonId) -> Coach:
    return Coach(
        id=CoachId.new(),
        person_id=person_id,
        role=CoachRole.HEAD_COACH,
        status=CoachStatus.ACTIVE,
    )


@pytest.fixture
def referee(person_id: PersonId) -> Referee:
    return Referee(
        id=RefereeId.new(),
        person_id=person_id,
        primary_role=RefereeRole.MAIN_REFEREE,
        status=RefereeStatus.ACTIVE,
    )