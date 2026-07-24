"""Testes dos enums específicos do People Context."""

import pytest

from ultrastats_ai.domain.shared import DomainValidationError

from ultrastats_ai.domain.people import (
    CoachRole,
    CoachStatus,
    PlayerStatus,
    RefereeCategory,
    RefereeRole,
    RefereeStatus,
)
from ultrastats_ai.domain.shared import DomainEnum


ENUM_CASES = (
    (
        PlayerStatus,
        (
            "youth",
            "amateur",
            "professional",
            "free_agent",
            "loaned",
            "suspended",
            "injured",
            "inactive",
            "retired",
            "unknown",
        ),
    ),
    (
        CoachRole,
        (
            "head_coach",
            "assistant_coach",
            "goalkeeper_coach",
            "fitness_coach",
            "technical_director",
            "interim_coach",
            "youth_coach",
            "other",
            "unknown",
        ),
    ),
    (
        CoachStatus,
        (
            "active",
            "unemployed",
            "suspended",
            "retired",
            "inactive",
            "unknown",
        ),
    ),
    (
        RefereeRole,
        (
            "main_referee",
            "assistant_referee",
            "fourth_official",
            "video_assistant_referee",
            "assistant_video_assistant_referee",
            "additional_assistant_referee",
            "reserve_assistant_referee",
            "referee_observer",
            "other",
            "unknown",
        ),
    ),
    (
        RefereeCategory,
        (
            "local",
            "regional",
            "national",
            "continental",
            "international",
            "elite",
            "amateur",
            "other",
            "unknown",
        ),
    ),
    (
        RefereeStatus,
        (
            "active",
            "inactive",
            "suspended",
            "temporarily_unavailable",
            "retired",
            "unknown",
        ),
    ),
)


@pytest.mark.parametrize(
    ("enum_type", "expected_values"),
    ENUM_CASES,
)
def test_people_enum_inherits_domain_enum(
    enum_type: type[DomainEnum],
    expected_values: tuple[str, ...],
) -> None:
    assert issubclass(enum_type, DomainEnum)
    assert tuple(member.value for member in enum_type) == (
        expected_values
    )


@pytest.mark.parametrize(
    ("enum_type", "expected_values"),
    ENUM_CASES,
)
def test_people_enum_string_representation(
    enum_type: type[DomainEnum],
    expected_values: tuple[str, ...],
) -> None:
    for member, expected in zip(
        enum_type,
        expected_values,
        strict=True,
    ):
        assert str(member) == expected


@pytest.mark.parametrize(
    ("enum_type", "expected_values"),
    ENUM_CASES,
)
def test_people_enum_parses_exact_values(
    enum_type: type[DomainEnum],
    expected_values: tuple[str, ...],
) -> None:
    for expected in expected_values:
        assert enum_type.parse(expected).value == expected


@pytest.mark.parametrize(
    ("enum_type", "expected_values"),
    ENUM_CASES,
)
def test_people_enum_parses_normalized_values(
    enum_type: type[DomainEnum],
    expected_values: tuple[str, ...],
) -> None:
    for expected in expected_values:
        formatted = expected.replace("_", " ").upper()

        assert enum_type.parse(formatted).value == expected


@pytest.mark.parametrize(
    "enum_type",
    [
        PlayerStatus,
        CoachRole,
        CoachStatus,
        RefereeRole,
        RefereeCategory,
        RefereeStatus,
    ],
)
def test_people_enum_rejects_unknown_value(
    enum_type: type[DomainEnum],
) -> None:
    with pytest.raises(DomainValidationError):
        enum_type.parse("invalid-value")

@pytest.mark.parametrize(
    "enum_type",
    [
        PlayerStatus,
        CoachRole,
        CoachStatus,
        RefereeRole,
        RefereeCategory,
        RefereeStatus,
    ],
)
def test_people_enum_rejects_non_string_parse_value(
    enum_type: type[DomainEnum],
) -> None:
    with pytest.raises(TypeError):
        enum_type.parse(123)