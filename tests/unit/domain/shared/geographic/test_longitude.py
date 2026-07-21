"""Testes de Longitude."""

from decimal import Decimal

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.geographic.longitude import Longitude


@pytest.mark.parametrize(
    "value",
    [
        -180,
        "-46.633308",
        0,
        "120.123456",
        180,
    ],
)
def test_longitude_accepts_values_inside_range(value: object) -> None:
    longitude = Longitude(value)  # type: ignore[arg-type]

    assert Decimal("-180") <= longitude.value <= Decimal("180")


@pytest.mark.parametrize(
    "value",
    [
        "-180.000001",
        -181,
        "180.000001",
        181,
    ],
)
def test_longitude_rejects_values_outside_range(value: object) -> None:
    with pytest.raises(
        DomainValidationError,
        match="Longitude deve estar entre -180 e 180",
    ):
        Longitude(value)  # type: ignore[arg-type]


def test_longitude_is_immutable() -> None:
    longitude = Longitude("-46.633308")

    with pytest.raises((AttributeError, TypeError)):
        longitude.value = Decimal("0")  # type: ignore[misc]