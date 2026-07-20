"""Testes do Value Object VenueName."""

from ultrastats_ai.domain.shared import (
    CityName,
    GeographicName,
    VenueName,
)
from ultrastats_ai.domain.shared.names import (
    VenueName as NamesPackageVenueName,
)
from ultrastats_ai.domain.shared.names.geography import (
    VenueName as GeographyPackageVenueName,
)


def test_venue_name_inherits_from_geographic_name() -> None:
    venue = VenueName("Maracanã")

    assert isinstance(venue, GeographicName)


def test_venue_name_normalizes_whitespace() -> None:
    venue = VenueName("  Allianz    Arena  ")

    assert venue.value == "Allianz Arena"


def test_venue_name_preserves_unicode_characters() -> None:
    venue = VenueName("Estádio do Maracanã")

    assert venue.value == "Estádio do Maracanã"


def test_venue_name_is_immutable() -> None:
    venue = VenueName("Wembley Stadium")

    try:
        venue.value = "Old Trafford"
    except (AttributeError, TypeError):
        pass
    else:
        raise AssertionError("VenueName deveria ser imutável")


def test_venue_name_equality_uses_value_and_type() -> None:
    first = VenueName("Maracanã")
    second = VenueName("Maracanã")

    assert first == second
    assert hash(first) == hash(second)


def test_venue_name_is_distinct_from_city_name() -> None:
    venue = VenueName("São Paulo")
    city = CityName("São Paulo")

    assert venue != city


def test_public_apis_export_same_venue_name_class() -> None:
    assert VenueName is NamesPackageVenueName
    assert VenueName is GeographyPackageVenueName