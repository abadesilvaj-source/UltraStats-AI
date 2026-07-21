"""Testes de Percentage."""

from decimal import Decimal

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.percentage import Percentage


@pytest.mark.parametrize("value", [0, 25, "50.5", 100])
def test_percentage_accepts_values_between_zero_and_one_hundred(
    value: object,
) -> None:
    percentage = Percentage(value)  # type: ignore[arg-type]

    assert Decimal("0") <= percentage.value <= Decimal("100")


@pytest.mark.parametrize("value", [-1, "100.01", 101])
def test_percentage_rejects_values_outside_range(value: object) -> None:
    with pytest.raises(
        DomainValidationError,
        match="Percentage deve estar entre 0 e 100",
    ):
        Percentage(value)  # type: ignore[arg-type]