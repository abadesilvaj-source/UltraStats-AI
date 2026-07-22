"""Testes da API pública do domínio geográfico."""

from ultrastats_ai.domain.geography import (
    AliasNotFoundError,
    Aliases,
    City,
    CityNameAliasConflictError,
    CityReconstruction,
    CityRepository,
    Country,
    CountryNameAliasConflictError,
    CountryReconstruction,
    CountryRepository,
    DuplicateAliasError,
    DuplicateExternalIdentityError,
    DuplicateHistoryFieldError,
    EmptyHistoryChangesError,
    ExternalIdentityNotFoundError,
    GeographyChangeType,
    GeographyDomainError,
    GeographyEntityKind,
    GeographyExternalIdentities,
    GeographyExternalIdentityError,
    GeographyExternalIdentityMapping,
    GeographyFieldChange,
    GeographyHistoryEntry,
    GeographyHistoryError,
    GeographyHistoryRepository,
    Region,
    RegionNameAliasConflictError,
    RegionReconstruction,
    RegionRepository,
    Stadium,
    StadiumNameAliasConflictError,
    StadiumReconstruction,
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
from ultrastats_ai.domain.geography.external_identity import (
    GeographyExternalIdentities as InternalGeographyExternalIdentities,
)
from ultrastats_ai.domain.geography.external_identity import (
    GeographyExternalIdentityMapping as InternalGeographyExternalIdentityMapping,
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
from ultrastats_ai.domain.geography.reconstruction import (
    CityReconstruction as InternalCityReconstruction,
)
from ultrastats_ai.domain.geography.reconstruction import (
    CountryReconstruction as InternalCountryReconstruction,
)
from ultrastats_ai.domain.geography.reconstruction import (
    RegionReconstruction as InternalRegionReconstruction,
)
from ultrastats_ai.domain.geography.reconstruction import (
    StadiumReconstruction as InternalStadiumReconstruction,
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


def test_external_identity_types_are_exported_by_public_api() -> None:
    assert (
        GeographyExternalIdentities
        is InternalGeographyExternalIdentities
    )

    assert (
        GeographyExternalIdentityMapping
        is InternalGeographyExternalIdentityMapping
    )


def test_reconstruction_types_are_exported_by_public_api() -> None:
    assert CityReconstruction is InternalCityReconstruction
    assert CountryReconstruction is InternalCountryReconstruction
    assert RegionReconstruction is InternalRegionReconstruction

    assert (
        StadiumReconstruction
        is InternalStadiumReconstruction
    )


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
    exported_errors = {
        AliasNotFoundError:
            geography_errors.AliasNotFoundError,
        CityNameAliasConflictError:
            geography_errors.CityNameAliasConflictError,
        CountryNameAliasConflictError:
            geography_errors.CountryNameAliasConflictError,
        DuplicateAliasError:
            geography_errors.DuplicateAliasError,
        DuplicateExternalIdentityError:
            geography_errors.DuplicateExternalIdentityError,
        DuplicateHistoryFieldError:
            geography_errors.DuplicateHistoryFieldError,
        EmptyHistoryChangesError:
            geography_errors.EmptyHistoryChangesError,
        ExternalIdentityNotFoundError:
            geography_errors.ExternalIdentityNotFoundError,
        GeographyDomainError:
            geography_errors.GeographyDomainError,
        GeographyExternalIdentityError:
            geography_errors.GeographyExternalIdentityError,
        GeographyHistoryError:
            geography_errors.GeographyHistoryError,
        RegionNameAliasConflictError:
            geography_errors.RegionNameAliasConflictError,
        StadiumNameAliasConflictError:
            geography_errors.StadiumNameAliasConflictError,
    }

    for public_error, internal_error in exported_errors.items():
        assert public_error is internal_error