"""Testes de Coordinates."""

from decimal import Decimal

import pytest

from ultrastats_ai.domain.shared.geographic.coordinates import Coordinates
from ultrastats_ai.domain.shared.geographic.latitude import Latitude
from ultrastats_ai.domain.shared.geographic.longitude import Longitude


def test_coordinates_stores_latitude_and_longitude() -> None:
    latitude = Latitude("-23.550520")
    longitude = Longitude("-46.633308")

    coordinates = Coordinates(
        latitude=latitude,
        longitude=longitude,
    )

    assert coordinates.latitude is latitude
    assert coordinates.longitude is longitude


def test_coordinates_rejects_raw_latitude() -> None:
    with pytest.raises(
        TypeError,
        match="latitude deve ser um objeto Latitude",
    ):
        Coordinates(
            latitude="-23.550520",  # type: ignore[arg-type]
            longitude=Longitude("-46.633308"),
        )


def test_coordinates_rejects_raw_longitude() -> None:
    with pytest.raises(
        TypeError,
        match="longitude deve ser um objeto Longitude",
    ):
        Coordinates(
            latitude=Latitude("-23.550520"),
            longitude="-46.633308",  # type: ignore[arg-type]
        )


def test_coordinates_exposes_decimal_pair() -> None:
    coordinates = Coordinates(
        latitude=Latitude("-23.550520"),
        longitude=Longitude("-46.633308"),
    )

    assert coordinates.decimal_pair == (
        Decimal("-23.550520"),
        Decimal("-46.633308"),
    )


def test_coordinates_exposes_text_pair() -> None:
    coordinates = Coordinates(
        latitude=Latitude("-23.550520"),
        longitude=Longitude("-46.633308"),
    )

    assert coordinates.text_pair == "-23.550520,-46.633308"


def test_coordinates_equality_uses_both_components() -> None:
    first = Coordinates(
        latitude=Latitude("-23.550520"),
        longitude=Longitude("-46.633308"),
    )
    second = Coordinates(
        latitude=Latitude("-23.550520"),
        longitude=Longitude("-46.633308"),
    )

    assert first == second
    assert hash(first) == hash(second)


def test_coordinates_is_immutable() -> None:
    coordinates = Coordinates(
        latitude=Latitude("-23.550520"),
        longitude=Longitude("-46.633308"),
    )

    with pytest.raises((AttributeError, TypeError)):
        coordinates.latitude = Latitude("0")  # type: ignore[misc]