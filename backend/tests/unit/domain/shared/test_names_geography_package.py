"""Testes do novo pacote de nomes geográficos."""

from ultrastats_ai.domain.shared.names import (
    CityName,
    CountryName,
    ProperName,
    RegionName,
)
from ultrastats_ai.domain.shared.names.geography import (
    CityName as GeographyCityName,
)
from ultrastats_ai.domain.shared.names.geography import (
    CountryName as GeographyCountryName,
)
from ultrastats_ai.domain.shared.names.geography import (
    RegionName as GeographyRegionName,
)


def test_names_package_exports_geography_names() -> None:
    assert CountryName is GeographyCountryName
    assert RegionName is GeographyRegionName
    assert CityName is GeographyCityName


def test_country_name_inherits_from_new_proper_name() -> None:
    name = CountryName("Brazil")

    assert isinstance(name, ProperName)


def test_region_name_inherits_from_new_proper_name() -> None:
    name = RegionName("São Paulo")

    assert isinstance(name, ProperName)


def test_city_name_inherits_from_new_proper_name() -> None:
    name = CityName("Araraquara")

    assert isinstance(name, ProperName)


def test_geography_names_normalize_whitespace() -> None:
    country = CountryName("  United    Kingdom  ")
    region = RegionName("  New    South Wales  ")
    city = CityName("  Buenos    Aires  ")

    assert country.value == "United Kingdom"
    assert region.value == "New South Wales"
    assert city.value == "Buenos Aires"


def test_geography_name_types_are_distinct() -> None:
    country = CountryName("São Paulo")
    region = RegionName("São Paulo")
    city = CityName("São Paulo")

    assert country != region
    assert country != city
    assert region != city