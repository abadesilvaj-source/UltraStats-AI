"""Testes da API pública do domínio geográfico."""

from ultrastats_ai.domain.geography import (
    AliasNotFoundError,
    Aliases,
    City,
    CityNameAliasConflictError,
    Country,
    CountryNameAliasConflictError,
    DuplicateAliasError,
    GeographyDomainError,
    Region,
    RegionNameAliasConflictError,
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
from ultrastats_ai.domain.geography.region import (
    Region as InternalRegion,
)


def test_geography_types_are_exported_by_public_api() -> None:
    assert Aliases is InternalAliases
    assert City is InternalCity
    assert Country is InternalCountry
    assert Region is InternalRegion

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
        GeographyDomainError
        is geography_errors.GeographyDomainError
    )

    assert (
        RegionNameAliasConflictError
        is geography_errors.RegionNameAliasConflictError
    )