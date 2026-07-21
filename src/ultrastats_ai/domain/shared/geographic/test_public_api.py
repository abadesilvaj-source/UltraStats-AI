"""Testes da API pública dos tipos geográficos."""

from ultrastats_ai.domain.shared import (
    Coordinates,
    Latitude,
    Longitude,
)
from ultrastats_ai.domain.shared.geographic import (
    Coordinates as GeographicCoordinates,
    Latitude as GeographicLatitude,
    Longitude as GeographicLongitude,
)


def test_geographic_types_are_exported_by_public_apis() -> None:
    assert Coordinates is GeographicCoordinates
    assert Latitude is GeographicLatitude
    assert Longitude is GeographicLongitude