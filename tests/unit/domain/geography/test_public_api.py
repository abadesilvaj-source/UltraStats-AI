"""Testes da API pública do domínio geográfico."""

from ultrastats_ai.domain.geography import (
    AliasNotFoundError,
    Aliases,
    Country,
    CountryNameAliasConflictError,
    DuplicateAliasError,
    GeographyDomainError,
)
from ultrastats_ai.domain.geography import errors as geography_errors
from ultrastats_ai.domain.geography.aliases import (
    Aliases as InternalAliases,
)
from ultrastats_ai.domain.geography.country import (
    Country as InternalCountry,
)


def test_geography_types_are_exported_by_public_api() -> None:
    assert Aliases is InternalAliases
    assert Country is InternalCountry
    assert (
        AliasNotFoundError
        is geography_errors.AliasNotFoundError
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