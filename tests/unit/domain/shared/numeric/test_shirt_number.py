"""Testes de ShirtNumber."""

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.shirt_number import ShirtNumber


@pytest.mark.parametrize("value", [1, "10", 99])
def test_shirt_number_accepts_values_between_one_and_ninety_nine(
    value: int | str,
) -> None:
    shirt_number = ShirtNumber(value)

    assert 1 <= shirt_number.value <= 99


@pytest.mark.parametrize("value", [0, -1, 100])
def test_shirt_number_rejects_values_outside_range(value: int) -> None:
    with pytest.raises(
        DomainValidationError,
        match="ShirtNumber deve estar entre 1 e 99",
    ):
        ShirtNumber(value)