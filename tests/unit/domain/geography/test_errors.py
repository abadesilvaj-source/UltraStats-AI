"""Testes das exceções do domínio geográfico."""

from ultrastats_ai.domain.geography.errors import (
    AliasNotFoundError,
    CityNameAliasConflictError,
    CountryNameAliasConflictError,
    DuplicateAliasError,
    DuplicateExternalIdentityError,
    DuplicateHistoryFieldError,
    EmptyHistoryChangesError,
    ExternalIdentityNotFoundError,
    GeographyDomainError,
    GeographyExternalIdentityError,
    GeographyHistoryError,
    RegionNameAliasConflictError,
    StadiumNameAliasConflictError,
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


def test_city_name_alias_conflict_error_inherits_from_geography_error() -> None:
    assert issubclass(
        CityNameAliasConflictError,
        GeographyDomainError,
    )


def test_stadium_name_alias_conflict_error_inherits_from_geography_error() -> None:
    assert issubclass(
        StadiumNameAliasConflictError,
        GeographyDomainError,
    )


def test_geography_history_error_inherits_from_geography_error() -> None:
    assert issubclass(
        GeographyHistoryError,
        GeographyDomainError,
    )


def test_duplicate_history_field_error_inherits_from_history_error() -> None:
    assert issubclass(
        DuplicateHistoryFieldError,
        GeographyHistoryError,
    )


def test_empty_history_changes_error_inherits_from_history_error() -> None:
    assert issubclass(
        EmptyHistoryChangesError,
        GeographyHistoryError,
    )

def test_geography_external_identity_error_inherits_from_geography_error() -> None:
    assert issubclass(
        GeographyExternalIdentityError,
        GeographyDomainError,
    )


def test_duplicate_external_identity_error_inherits_from_external_identity_error() -> None:
    assert issubclass(
        DuplicateExternalIdentityError,
        GeographyExternalIdentityError,
    )

def test_external_identity_not_found_error_inherits_from_external_identity_error() -> None:
    assert issubclass(
        ExternalIdentityNotFoundError,
        GeographyExternalIdentityError,
    )