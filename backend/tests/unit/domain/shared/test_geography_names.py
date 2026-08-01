"""Testes de diferenciação semântica entre nomes geográficos."""

from ultrastats_ai.domain.shared.city_name import CityName
from ultrastats_ai.domain.shared.country_name import CountryName
from ultrastats_ai.domain.shared.region_name import RegionName


def test_geography_name_types_are_semantically_distinct() -> None:
    country_name = CountryName("São Paulo")
    region_name = RegionName("São Paulo")
    city_name = CityName("São Paulo")

    assert country_name != region_name
    assert country_name != city_name
    assert region_name != city_name


def test_equal_country_names_have_equal_hashes() -> None:
    first = CountryName("Brazil")
    second = CountryName("  Brazil  ")

    assert first == second
    assert hash(first) == hash(second)