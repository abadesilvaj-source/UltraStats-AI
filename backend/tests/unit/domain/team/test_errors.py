"""Testes dos erros específicos do Team Context."""

import pytest

from ultrastats_ai.domain.shared import DomainValidationError
from ultrastats_ai.domain.team import (
    DuplicateSquadNumberError,
    DuplicateTeamAliasError,
    InvalidMembershipPeriodError,
    InvalidMembershipStateError,
    InvalidRegistrationPeriodError,
    InvalidRegistrationStateError,
    SquadRegistrationAlreadyExistsError,
    SquadRegistrationNotFoundError,
    SquadRegistrationOwnershipError,
    TeamAlreadyActiveError,
    TeamAlreadyInactiveError,
    TeamAliasNotFoundError,
    TeamDomainError,
    TeamMembershipAlreadyExistsError,
    TeamMembershipNotFoundError,
    TeamMembershipOwnershipError,
    TeamNameAliasConflictError,
)


TEAM_ERRORS = (
    DuplicateSquadNumberError,
    DuplicateTeamAliasError,
    InvalidMembershipPeriodError,
    InvalidMembershipStateError,
    InvalidRegistrationPeriodError,
    InvalidRegistrationStateError,
    SquadRegistrationAlreadyExistsError,
    SquadRegistrationNotFoundError,
    SquadRegistrationOwnershipError,
    TeamAlreadyActiveError,
    TeamAlreadyInactiveError,
    TeamAliasNotFoundError,
    TeamMembershipAlreadyExistsError,
    TeamMembershipNotFoundError,
    TeamMembershipOwnershipError,
    TeamNameAliasConflictError,
)


def test_team_domain_error_inherits_domain_validation_error() -> None:
    assert issubclass(
        TeamDomainError,
        DomainValidationError,
    )


@pytest.mark.parametrize(
    "error_type",
    TEAM_ERRORS,
)
def test_team_specific_errors_inherit_team_domain_error(
    error_type: type[TeamDomainError],
) -> None:
    assert issubclass(
        error_type,
        TeamDomainError,
    )


@pytest.mark.parametrize(
    "error_type",
    TEAM_ERRORS,
)
def test_team_errors_preserve_message(
    error_type: type[TeamDomainError],
) -> None:
    error = error_type("Mensagem de teste.")

    assert str(error) == "Mensagem de teste."