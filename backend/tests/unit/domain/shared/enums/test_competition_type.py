"""Testes de CompetitionType."""

import pytest

from ultrastats_ai.domain.shared.enums.competition_type import (
    CompetitionType,
)
from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_competition_type_inherits_from_domain_enum() -> None:
    assert issubclass(CompetitionType, DomainEnum)


def test_competition_type_contains_expected_values() -> None:
    assert CompetitionType.values() == (
        "league",
        "cup",
        "tournament",
        "playoff",
        "friendly",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("league", CompetitionType.LEAGUE),
        ("LEAGUE", CompetitionType.LEAGUE),
        ("Cup", CompetitionType.CUP),
        ("PLAYOFF", CompetitionType.PLAYOFF),
        (" friendly ", CompetitionType.FRIENDLY),
    ],
)
def test_competition_type_parses_valid_values(
    value: str,
    expected: CompetitionType,
) -> None:
    assert CompetitionType.parse(value) is expected


def test_competition_type_rejects_invalid_value() -> None:
    with pytest.raises(DomainValidationError):
        CompetitionType.parse("unknown")