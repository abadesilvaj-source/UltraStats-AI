"""Testes do tipo canônico CompetitionCode."""

import pytest

from ultrastats_ai.domain.shared import CompetitionCode
from ultrastats_ai.domain.shared.codes import (
    CompetitionCode as CodesPackageCompetitionCode,
)
from ultrastats_ai.domain.shared.codes.code_value import CodeValue


def test_competition_code_inherits_from_code_value() -> None:
    code = CompetitionCode("BR_SERIE_A")

    assert isinstance(code, CodeValue)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("BR_SERIE_A", "BR_SERIE_A"),
        ("br_serie_a", "BR_SERIE_A"),
        (" uefa_champions_league ", "UEFA_CHAMPIONS_LEAGUE"),
        ("FIFA-CLUB-WORLD-CUP", "FIFA-CLUB-WORLD-CUP"),
        ("COMPETITION.001", "COMPETITION.001"),
    ],
)
def test_competition_code_accepts_and_normalizes_valid_values(
    value: str,
    expected: str,
) -> None:
    code = CompetitionCode(value)

    assert code.value == expected


@pytest.mark.parametrize(
    "value",
    [
        "BR SERIE A",
        "BR/SERIE/A",
        "SÉRIE_A",
        "BR#1",
        "",
        "   ",
    ],
)
def test_competition_code_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        CompetitionCode(value)


def test_competition_code_equality_uses_normalized_value() -> None:
    first = CompetitionCode("br_serie_a")
    second = CompetitionCode("BR_SERIE_A")

    assert first == second
    assert hash(first) == hash(second)


def test_competition_code_is_immutable() -> None:
    code = CompetitionCode("BR_SERIE_A")

    with pytest.raises((AttributeError, TypeError)):
        code.value = "BR_SERIE_B"  # type: ignore[misc]


def test_competition_code_public_apis_export_same_class() -> None:
    assert CompetitionCode is CodesPackageCompetitionCode