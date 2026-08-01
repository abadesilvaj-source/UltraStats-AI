"""Testes de Height."""

from decimal import Decimal

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.height import Height


@pytest.mark.parametrize("value", ["1", 170, "182.5", 300])
def test_height_accepts_valid_centimeter_values(value: object) -> None:
    height = Height(value)  # type: ignore[arg-type]

    assert Decimal("0") < height.value <= Decimal("300")


@pytest.mark.parametrize("value", [0, -1, "300.01"])
def test_height_rejects_invalid_values(value: object) -> None:
    with pytest.raises(
        DomainValidationError,
        match="até 300 centímetros",
    ):
        Height(value)  # type: ignore[arg-type]


def test_height_converts_centimeters_to_meters() -> None:
    height = Height("182")

    assert height.meters == Decimal("1.82")