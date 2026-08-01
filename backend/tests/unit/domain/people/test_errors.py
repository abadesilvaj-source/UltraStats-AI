"""Testes dos erros específicos do People Context."""

import pytest

from ultrastats_ai.domain.people import (
    DuplicatePersonAliasError,
    InvalidProfessionalPeriodError,
    InvalidRetirementStateError,
    PeopleDomainError,
    PersonAliasNotFoundError,
    PersonNameAliasConflictError,
    PersonProfileAlreadyExistsError,
    PersonProfileNotFoundError,
    PersonAlreadyActiveError,
    PersonAlreadyInactiveError,
    PersonProfileOwnershipError,
)
from ultrastats_ai.domain.shared import DomainValidationError


PEOPLE_ERRORS = (
    DuplicatePersonAliasError,
    InvalidProfessionalPeriodError,
    InvalidRetirementStateError,
    PersonAliasNotFoundError,
    PersonAlreadyActiveError,
    PersonAlreadyInactiveError,
    PersonNameAliasConflictError,
    PersonProfileAlreadyExistsError,
    PersonProfileNotFoundError,
    PersonProfileOwnershipError,
)


def test_people_domain_error_inherits_domain_validation_error() -> None:
    assert issubclass(
        PeopleDomainError,
        DomainValidationError,
    )


@pytest.mark.parametrize(
    "error_type",
    PEOPLE_ERRORS,
)
def test_specific_people_error_inherits_people_domain_error(
    error_type: type[PeopleDomainError],
) -> None:
    assert issubclass(
        error_type,
        PeopleDomainError,
    )


@pytest.mark.parametrize(
    "error_type",
    PEOPLE_ERRORS,
)
def test_people_error_preserves_message(
    error_type: type[PeopleDomainError],
) -> None:
    error = error_type("mensagem de teste")

    assert str(error) == "mensagem de teste"


@pytest.mark.parametrize(
    "error_type",
    PEOPLE_ERRORS,
)
def test_people_error_can_be_raised(
    error_type: type[PeopleDomainError],
) -> None:
    with pytest.raises(
        error_type,
        match="erro esperado",
    ):
        raise error_type("erro esperado")