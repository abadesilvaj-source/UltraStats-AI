"""Testes de ParticipantRole."""

import pytest

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.participant_role import (
    ParticipantRole,
)
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_participant_role_inherits_from_domain_enum() -> None:
    assert issubclass(ParticipantRole, DomainEnum)


def test_participant_role_contains_expected_values() -> None:
    assert ParticipantRole.values() == (
        "home",
        "away",
        "neutral",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("home", ParticipantRole.HOME),
        ("HOME", ParticipantRole.HOME),
        (" Home ", ParticipantRole.HOME),
        ("away", ParticipantRole.AWAY),
        ("AWAY", ParticipantRole.AWAY),
        ("neutral", ParticipantRole.NEUTRAL),
    ],
)
def test_participant_role_parses_valid_values(
    value: str,
    expected: ParticipantRole,
) -> None:
    assert ParticipantRole.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "host",
        "visitor",
        "unknown",
    ],
)
def test_participant_role_rejects_invalid_values(value: str) -> None:
    with pytest.raises(DomainValidationError):
        ParticipantRole.parse(value)


def test_participant_role_returns_expected_choices() -> None:
    assert ParticipantRole.choices() == (
        ("home", "HOME"),
        ("away", "AWAY"),
        ("neutral", "NEUTRAL"),
    )


def test_participant_role_is_serializable_as_string() -> None:
    assert str(ParticipantRole.HOME) == "home"
    assert ParticipantRole.HOME.value == "home"