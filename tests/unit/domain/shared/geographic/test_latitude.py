"""Testes de Latitude."""

from decimal import Decimal

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.geographic.latitude import Latitude


@pytest.mark.parametrize(
    "value",
    [
        -90,
        "-23.550520",
        0,
        "45.123456",
        90,
    ],
)
def test_latitude_accepts_values_inside_range(value: object) -> None:
    latitude = Latitude(value)  # type: ignore[arg-type]

    assert Decimal("-90") <= latitude.value <= Decimal("90")


@pytest.mark.parametrize(
    "value",
    [
        "-90.000001",
        -91,
        "90.000001",
        91,
    ],
)
def test_latitude_rejects_values_outside_range(value: object) -> None:
    with pytest.raises(
        DomainValidationError,
        match="Latitude deve estar entre -90 e 90",
    ):
        Latitude(value)  # type: ignore[arg-type]


def test_latitude_is_immutable() -> None:
    latitude = Latitude("-23.550520")

    with pytest.raises((AttributeError, TypeError)):
        latitude.value = Decimal("0")  # type: ignore[misc]