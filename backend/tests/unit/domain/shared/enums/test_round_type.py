"""Testes de RoundType."""

import pytest

from ultrastats_ai.domain.shared.enums.round_type import RoundType
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_round_type_contains_expected_values() -> None:
    assert RoundType.values() == (
        "regular",
        "preliminary",
        "qualifying",
        "group",
        "knockout",
        "playoff",
        "final",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("regular", RoundType.REGULAR),
        ("PRELIMINARY", RoundType.PRELIMINARY),
        ("Qualifying", RoundType.QUALIFYING),
        (" group ", RoundType.GROUP),
        ("knockout", RoundType.KNOCKOUT),
        ("PLAYOFF", RoundType.PLAYOFF),
        ("final", RoundType.FINAL),
    ],
)
def test_round_type_parses_valid_values(
    value: str,
    expected: RoundType,
) -> None:
    assert RoundType.parse(value) is expected


def test_round_type_rejects_invalid_value() -> None:
    with pytest.raises(DomainValidationError):
        RoundType.parse("unknown_round")