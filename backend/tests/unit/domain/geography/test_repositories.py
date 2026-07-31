"""Testes dos contratos de repositório geográfico."""

import inspect

from ultrastats_ai.domain.geography import (
    CityRepository,
    CountryRepository,
    GeographyHistoryRepository,
    RegionRepository,
    StadiumRepository,
)


def public_methods(protocol: type[object]) -> set[str]:
    """Retorna os métodos públicos definidos no protocolo."""
    return {
        name
        for name, member in inspect.getmembers(
            protocol,
            predicate=inspect.isfunction,
        )
        if not name.startswith("_")
    }


def test_country_repository_contract() -> None:
    assert public_methods(CountryRepository) == {
        "delete",
        "get_by_id",
        "list_all",
        "save",
    }


def test_region_repository_contract() -> None:
    assert public_methods(RegionRepository) == {
        "delete",
        "get_by_id",
        "list_by_country",
        "save",
    }


def test_city_repository_contract() -> None:
    assert public_methods(CityRepository) == {
        "delete",
        "get_by_id",
        "list_by_country",
        "list_by_region",
        "save",
    }


def test_stadium_repository_contract() -> None:
    assert public_methods(StadiumRepository) == {
        "delete",
        "get_by_id",
        "list_by_city",
        "list_by_country",
        "list_by_region",
        "save",
    }


def test_geography_history_repository_contract() -> None:
    assert public_methods(GeographyHistoryRepository) == {
        "append",
        "get_by_id",
        "list_for_entity",
    }


def test_repository_contracts_are_protocols() -> None:
    repositories = (
        CountryRepository,
        RegionRepository,
        CityRepository,
        StadiumRepository,
        GeographyHistoryRepository,
    )

    for repository in repositories:
        assert getattr(
            repository,
            "_is_protocol",
            False,
        )