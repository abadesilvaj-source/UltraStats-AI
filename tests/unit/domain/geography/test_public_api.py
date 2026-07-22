"""Testes da API pública do domínio geográfico."""

from ultrastats_ai.domain.geography import (
    AliasNotFoundError,
    Aliases,
    City,
    CityNameAliasConflictError,
    CityRepository,
    Country,
    CountryNameAliasConflictError,
    CountryRepository,
    DuplicateAliasError,
    DuplicateHistoryFieldError,
    EmptyHistoryChangesError,
    GeographyChangeType,
    GeographyDomainError,
    GeographyEntityKind,
    GeographyFieldChange,
    GeographyHistoryEntry,
    GeographyHistoryError,
    GeographyHistoryRepository,
    Region,
    RegionNameAliasConflictError,
    RegionRepository,
    Stadium,
    StadiumNameAliasConflictError,
    StadiumRepository,
)
from ultrastats_ai.domain.geography import errors as geography_errors
from ultrastats_ai.domain.geography.aliases import (
    Aliases as InternalAliases,
)
from ultrastats_ai.domain.geography.city import (
    City as InternalCity,
)
from ultrastats_ai.domain.geography.country import (
    Country as InternalCountry,
)
from ultrastats_ai.domain.geography.history import (
    GeographyChangeType as InternalGeographyChangeType,
)
from ultrastats_ai.domain.geography.history import (
    GeographyEntityKind as InternalGeographyEntityKind,
)
from ultrastats_ai.domain.geography.history import (
    GeographyFieldChange as InternalGeographyFieldChange,
)
from ultrastats_ai.domain.geography.history import (
    GeographyHistoryEntry as InternalGeographyHistoryEntry,
)
from ultrastats_ai.domain.geography.region import (
    Region as InternalRegion,
)
from ultrastats_ai.domain.geography.repositories import (
    CityRepository as InternalCityRepository,
)
from ultrastats_ai.domain.geography.repositories import (
    CountryRepository as InternalCountryRepository,
)
from ultrastats_ai.domain.geography.repositories import (
    GeographyHistoryRepository as InternalGeographyHistoryRepository,
)
from ultrastats_ai.domain.geography.repositories import (
    RegionRepository as InternalRegionRepository,
)
from ultrastats_ai.domain.geography.repositories import (
    StadiumRepository as InternalStadiumRepository,
)
from ultrastats_ai.domain.geography.stadium import (
    Stadium as InternalStadium,
)


def test_geography_entities_are_exported_by_public_api() -> None:
    assert Aliases is InternalAliases
    assert City is InternalCity
    assert Country is InternalCountry
    assert Region is InternalRegion
    assert Stadium is InternalStadium


def test_geography_history_types_are_exported_by_public_api() -> None:
    assert GeographyChangeType is InternalGeographyChangeType
    assert GeographyEntityKind is InternalGeographyEntityKind
    assert GeographyFieldChange is InternalGeographyFieldChange
    assert GeographyHistoryEntry is InternalGeographyHistoryEntry


def test_geography_repositories_are_exported_by_public_api() -> None:
    assert CityRepository is InternalCityRepository
    assert CountryRepository is InternalCountryRepository

    assert (
        GeographyHistoryRepository
        is InternalGeographyHistoryRepository
    )

    assert RegionRepository is InternalRegionRepository
    assert StadiumRepository is InternalStadiumRepository


def test_geography_errors_are_exported_by_public_api() -> None:
    assert (
        AliasNotFoundError
        is geography_errors.AliasNotFoundError
    )

    assert (
        CityNameAliasConflictError
        is geography_errors.CityNameAliasConflictError
    )

    assert (
        CountryNameAliasConflictError
        is geography_errors.CountryNameAliasConflictError
    )

    assert (
        DuplicateAliasError
        is geography_errors.DuplicateAliasError
    )

    assert (
        DuplicateHistoryFieldError
        is geography_errors.DuplicateHistoryFieldError
    )

    assert (
        EmptyHistoryChangesError
        is geography_errors.EmptyHistoryChangesError
    )

    assert (
        GeographyDomainError
        is geography_errors.GeographyDomainError
    )

    assert (
        GeographyHistoryError
        is geography_errors.GeographyHistoryError
    )

    assert (
        RegionNameAliasConflictError
        is geography_errors.RegionNameAliasConflictError
    )

    assert (
        StadiumNameAliasConflictError
        is geography_errors.StadiumNameAliasConflictError
    )