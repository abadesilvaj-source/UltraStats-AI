"""Testes dos enums de histórico do People Context."""

import pytest

from ultrastats_ai.domain.people import (
    PeopleHistoryAction,
    PeopleProfileType,
)
from ultrastats_ai.domain.shared import (
    DomainValidationError,
)


@pytest.mark.parametrize(
    ("member", "expected"),
    [
        (
            PeopleHistoryAction.PERSON_CREATED,
            "person_created",
        ),
        (
            PeopleHistoryAction.PERSON_RENAMED,
            "person_renamed",
        ),
        (
            PeopleHistoryAction.ALIAS_ADDED,
            "alias_added",
        ),
        (
            PeopleHistoryAction.PLAYER_PROFILE_ADDED,
            "player_profile_added",
        ),
        (
            PeopleHistoryAction.PERSON_DEACTIVATED,
            "person_deactivated",
        ),
    ],
)
def test_history_action_values(
    member: PeopleHistoryAction,
    expected: str,
) -> None:
    assert member.value == expected


@pytest.mark.parametrize(
    "profile_type",
    list(PeopleProfileType),
)
def test_profile_type_parses_known_values(
    profile_type: PeopleProfileType,
) -> None:
    assert (
        PeopleProfileType.parse(profile_type.value)
        is profile_type
    )


def test_history_action_rejects_unknown_value() -> None:
    with pytest.raises(DomainValidationError):
        PeopleHistoryAction.parse("unknown-action")


def test_profile_type_rejects_unknown_value() -> None:
    with pytest.raises(DomainValidationError):
        PeopleProfileType.parse("unknown-profile")