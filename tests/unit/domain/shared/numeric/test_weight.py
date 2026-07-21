"""Testes de Weight."""

from decimal import Decimal

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.weight import Weight


@pytest.mark.parametrize("value", ["1", 70, "82.5", 500])
def test_weight_accepts_valid_kilogram_values(value: object) -> None:
    weight = Weight(value)  # type: ignore[arg-type]

    assert Decimal("0") < weight.value <= Decimal("500")


@pytest.mark.parametrize("value", [0, -1, "500.01"])
def test_weight_rejects_invalid_values(value: object) -> None:
    with pytest.raises(
        DomainValidationError,
        match="até 500 quilogramas",
    ):
        Weight(value)  # type: ignore[arg-type]