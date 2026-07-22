"""Testes das exceções do domínio geográfico."""

from ultrastats_ai.domain.geography.errors import (
    AliasNotFoundError,
    CountryNameAliasConflictError,
    DuplicateAliasError,
    GeographyDomainError,
    RegionNameAliasConflictError,
)
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_geography_domain_error_inherits_from_domain_validation_error() -> None:
    assert issubclass(
        GeographyDomainError,
        DomainValidationError,
    )


def test_duplicate_alias_error_inherits_from_geography_error() -> None:
    assert issubclass(
        DuplicateAliasError,
        GeographyDomainError,
    )


def test_alias_not_found_error_inherits_from_geography_error() -> None:
    assert issubclass(
        AliasNotFoundError,
        GeographyDomainError,
    )


def test_country_name_alias_conflict_error_inherits_from_geography_error() -> None:
    assert issubclass(
        CountryNameAliasConflictError,
        GeographyDomainError,
    )


def test_region_name_alias_conflict_error_inherits_from_geography_error() -> None:
    assert issubclass(
        RegionNameAliasConflictError,
        GeographyDomainError,
    )