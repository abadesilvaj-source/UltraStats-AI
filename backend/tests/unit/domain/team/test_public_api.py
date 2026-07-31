"""Testes da API pública do Team Context."""

from ultrastats_ai.domain.team import (
    DuplicateSquadNumberError,
    InvalidTeamPeriodError,
    MembershipRole,
    MembershipStatus,
    SquadRegistration,
    SquadRegistrationAlreadyExistsError,
    SquadRegistrationNotFoundError,
    SquadRegistrationOwnershipError,
    SquadRegistrationStatus,
    Team,
    TeamAliases,
    TeamAlreadyActiveError,
    TeamAlreadyInactiveError,
    TeamMembership,
    TeamMembershipAlreadyExistsError,
    TeamMembershipNotFoundError,
    TeamMembershipOwnershipError,
    TeamNameAliasConflictError,
    TeamStatus,
    TeamType,
)
from ultrastats_ai.domain.team.aliases import (
    TeamAliases as InternalTeamAliases,
)
from ultrastats_ai.domain.team.enums import (
    MembershipRole as InternalMembershipRole,
)
from ultrastats_ai.domain.team.enums import (
    MembershipStatus as InternalMembershipStatus,
)
from ultrastats_ai.domain.team.enums import (
    SquadRegistrationStatus as InternalSquadRegistrationStatus,
)
from ultrastats_ai.domain.team.enums import (
    TeamStatus as InternalTeamStatus,
)
from ultrastats_ai.domain.team.enums import (
    TeamType as InternalTeamType,
)
from ultrastats_ai.domain.team.errors import (
    DuplicateSquadNumberError as InternalDuplicateSquadNumberError,
)
from ultrastats_ai.domain.team.errors import (
    InvalidTeamPeriodError as InternalInvalidTeamPeriodError,
)
from ultrastats_ai.domain.team.errors import (
    SquadRegistrationAlreadyExistsError
    as InternalSquadRegistrationAlreadyExistsError,
)
from ultrastats_ai.domain.team.errors import (
    SquadRegistrationNotFoundError
    as InternalSquadRegistrationNotFoundError,
)
from ultrastats_ai.domain.team.errors import (
    SquadRegistrationOwnershipError
    as InternalSquadRegistrationOwnershipError,
)
from ultrastats_ai.domain.team.errors import (
    TeamAlreadyActiveError as InternalTeamAlreadyActiveError,
)
from ultrastats_ai.domain.team.errors import (
    TeamAlreadyInactiveError as InternalTeamAlreadyInactiveError,
)
from ultrastats_ai.domain.team.errors import (
    TeamMembershipAlreadyExistsError
    as InternalTeamMembershipAlreadyExistsError,
)
from ultrastats_ai.domain.team.errors import (
    TeamMembershipNotFoundError
    as InternalTeamMembershipNotFoundError,
)
from ultrastats_ai.domain.team.errors import (
    TeamMembershipOwnershipError
    as InternalTeamMembershipOwnershipError,
)
from ultrastats_ai.domain.team.errors import (
    TeamNameAliasConflictError
    as InternalTeamNameAliasConflictError,
)
from ultrastats_ai.domain.team.membership import (
    TeamMembership as InternalTeamMembership,
)
from ultrastats_ai.domain.team.registration import (
    SquadRegistration as InternalSquadRegistration,
)
from ultrastats_ai.domain.team.team import Team as InternalTeam


def test_public_api_exports_team_aggregate() -> None:
    """Exporta o Aggregate Root pela API pública."""

    assert Team is InternalTeam


def test_public_api_exports_team_aliases() -> None:
    """Exporta a coleção de aliases pela API pública."""

    assert TeamAliases is InternalTeamAliases


def test_public_api_exports_team_membership() -> None:
    """Exporta a entidade de vínculo pela API pública."""

    assert TeamMembership is InternalTeamMembership


def test_public_api_exports_squad_registration() -> None:
    """Exporta a entidade de inscrição pela API pública."""

    assert SquadRegistration is InternalSquadRegistration


def test_public_api_exports_team_enums() -> None:
    """Exporta os enums do Team Context."""

    assert TeamType is InternalTeamType
    assert TeamStatus is InternalTeamStatus
    assert MembershipRole is InternalMembershipRole
    assert MembershipStatus is InternalMembershipStatus
    assert (
        SquadRegistrationStatus
        is InternalSquadRegistrationStatus
    )


def test_public_api_exports_team_errors() -> None:
    """Exporta os erros do Team Context."""

    assert (
        DuplicateSquadNumberError
        is InternalDuplicateSquadNumberError
    )
    assert (
        InvalidTeamPeriodError
        is InternalInvalidTeamPeriodError
    )
    assert (
        SquadRegistrationAlreadyExistsError
        is InternalSquadRegistrationAlreadyExistsError
    )
    assert (
        SquadRegistrationNotFoundError
        is InternalSquadRegistrationNotFoundError
    )
    assert (
        SquadRegistrationOwnershipError
        is InternalSquadRegistrationOwnershipError
    )
    assert (
        TeamAlreadyActiveError
        is InternalTeamAlreadyActiveError
    )
    assert (
        TeamAlreadyInactiveError
        is InternalTeamAlreadyInactiveError
    )
    assert (
        TeamMembershipAlreadyExistsError
        is InternalTeamMembershipAlreadyExistsError
    )
    assert (
        TeamMembershipNotFoundError
        is InternalTeamMembershipNotFoundError
    )
    assert (
        TeamMembershipOwnershipError
        is InternalTeamMembershipOwnershipError
    )
    assert (
        TeamNameAliasConflictError
        is InternalTeamNameAliasConflictError
    )

def test_public_api_declares_expected_exports() -> None:
    """Declara explicitamente todos os nomes públicos."""

    import ultrastats_ai.domain.team as team_context

    expected_exports = {
    "DuplicateSquadNumberError",
    "DuplicateTeamAliasError",
    "InvalidMembershipPeriodError",
    "InvalidMembershipStateError",
    "InvalidRegistrationPeriodError",
    "InvalidRegistrationStateError",
    "InvalidTeamPeriodError",
    "MembershipRole",
    "MembershipStatus",
    "SquadRegistration",
    "SquadRegistrationAlreadyExistsError",
    "SquadRegistrationNotFoundError",
    "SquadRegistrationOwnershipError",
    "SquadRegistrationStatus",
    "Team",
    "TeamAliases",
    "TeamAliasNotFoundError",
    "TeamAlreadyActiveError",
    "TeamAlreadyInactiveError",
    "TeamDomainError",
    "TeamMembership",
    "TeamMembershipAlreadyExistsError",
    "TeamMembershipNotFoundError",
    "TeamMembershipOwnershipError",
    "TeamNameAliasConflictError",
    "TeamStatus",
    "TeamType",
}

    assert set(team_context.__all__) == expected_exports