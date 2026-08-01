"""Testes dos enums fundamentais do Team Context."""

import pytest

from ultrastats_ai.domain.shared import DomainValidationError
from ultrastats_ai.domain.team import (
    MembershipRole,
    MembershipStatus,
    SquadRegistrationStatus,
    TeamStatus,
    TeamType,
)


ENUM_TYPES = (
    TeamType,
    TeamStatus,
    MembershipRole,
    MembershipStatus,
    SquadRegistrationStatus,
)


@pytest.mark.parametrize(
    "enum_type",
    ENUM_TYPES,
)
def test_team_enums_have_members(
    enum_type: type,
) -> None:
    assert list(enum_type)


@pytest.mark.parametrize(
    "enum_type",
    ENUM_TYPES,
)
def test_team_enums_have_unique_values(
    enum_type: type,
) -> None:
    values = [
        member.value
        for member in enum_type
    ]

    assert len(values) == len(set(values))


@pytest.mark.parametrize(
    "enum_type",
    ENUM_TYPES,
)
def test_team_enums_use_non_empty_string_values(
    enum_type: type,
) -> None:
    for member in enum_type:
        assert isinstance(member.value, str)
        assert member.value
        assert member.value == member.value.strip()


@pytest.mark.parametrize(
    "enum_type",
    ENUM_TYPES,
)
def test_team_enums_parse_all_known_values(
    enum_type: type,
) -> None:
    for member in enum_type:
        assert enum_type.parse(member.value) is member


@pytest.mark.parametrize(
    "enum_type",
    ENUM_TYPES,
)
def test_team_enums_reject_unknown_value(
    enum_type: type,
) -> None:
    with pytest.raises(DomainValidationError):
        enum_type.parse("invalid-value")


@pytest.mark.parametrize(
    ("member", "expected"),
    [
        (TeamType.CLUB, "club"),
        (
            TeamType.NATIONAL_TEAM,
            "national_team",
        ),
        (
            TeamType.YOUTH_TEAM,
            "youth_team",
        ),
        (TeamStatus.ACTIVE, "active"),
        (
            TeamStatus.DISSOLVED,
            "dissolved",
        ),
        (
            MembershipRole.PLAYER,
            "player",
        ),
        (
            MembershipRole.HEAD_COACH,
            "head_coach",
        ),
        (
            MembershipRole.PHYSIOTHERAPIST,
            "physiotherapist",
        ),
        (
            MembershipStatus.ACTIVE,
            "active",
        ),
        (
            MembershipStatus.ENDED,
            "ended",
        ),
        (
            SquadRegistrationStatus.REGISTERED,
            "registered",
        ),
        (
            SquadRegistrationStatus.INELIGIBLE,
            "ineligible",
        ),
    ],
)
def test_team_enum_canonical_values(
    member: object,
    expected: str,
) -> None:
    assert member.value == expected