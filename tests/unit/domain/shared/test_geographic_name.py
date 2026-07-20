"""Testes do tipo base GeographicName."""

from ultrastats_ai.domain.shared import (
    CityName,
    CountryName,
    GeographicName,
    ProperName,
    RegionName,
)


def test_geographic_name_inherits_from_proper_name() -> None:
    name = GeographicName("South America")

    assert isinstance(name, ProperName)


def test_geographic_name_normalizes_whitespace() -> None:
    name = GeographicName("  South    America  ")

    assert name.value == "South America"


def test_country_name_inherits_from_geographic_name() -> None:
    name = CountryName("Brazil")

    assert isinstance(name, GeographicName)


def test_region_name_inherits_from_geographic_name() -> None:
    name = RegionName("São Paulo")

    assert isinstance(name, GeographicName)


def test_city_name_inherits_from_geographic_name() -> None:
    name = CityName("Araraquara")

    assert isinstance(name, GeographicName)


def test_geographic_name_types_remain_semantically_distinct() -> None:
    country = CountryName("São Paulo")
    region = RegionName("São Paulo")
    city = CityName("São Paulo")

    assert country != region
    assert country != city
    assert region != city