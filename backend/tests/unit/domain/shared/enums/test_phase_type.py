"""Testes de PhaseType."""

import pytest

from ultrastats_ai.domain.shared.enums.phase_type import PhaseType
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_phase_type_contains_expected_values() -> None:
    assert PhaseType.values() == (
        "qualifying",
        "league_stage",
        "group_stage",
        "round_of_32",
        "round_of_16",
        "quarter_final",
        "semi_final",
        "third_place",
        "final",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("qualifying", PhaseType.QUALIFYING),
        ("League Stage", PhaseType.LEAGUE_STAGE),
        ("GROUP-STAGE", PhaseType.GROUP_STAGE),
        ("round of 16", PhaseType.ROUND_OF_16),
        ("Quarter Final", PhaseType.QUARTER_FINAL),
        ("SEMI_FINAL", PhaseType.SEMI_FINAL),
        ("third place", PhaseType.THIRD_PLACE),
        ("final", PhaseType.FINAL),
    ],
)
def test_phase_type_parses_valid_values(
    value: str,
    expected: PhaseType,
) -> None:
    assert PhaseType.parse(value) is expected


def test_phase_type_rejects_invalid_value() -> None:
    with pytest.raises(DomainValidationError):
        PhaseType.parse("unknown_phase")