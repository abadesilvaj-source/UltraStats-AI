"""API pública do Team Context."""

from ultrastats_ai.domain.team.aliases import TeamAliases
from ultrastats_ai.domain.team.enums import (
    MembershipRole,
    MembershipStatus,
    SquadRegistrationStatus,
    TeamStatus,
    TeamType,
)
from ultrastats_ai.domain.team.errors import (
    DuplicateSquadNumberError,
    DuplicateTeamAliasError,
    InvalidMembershipPeriodError,
    InvalidMembershipStateError,
    InvalidRegistrationPeriodError,
    InvalidRegistrationStateError,
    InvalidTeamPeriodError,
    SquadRegistrationAlreadyExistsError,
    SquadRegistrationNotFoundError,
    SquadRegistrationOwnershipError,
    TeamAliasNotFoundError,
    TeamAlreadyActiveError,
    TeamAlreadyInactiveError,
    TeamDomainError,
    TeamMembershipAlreadyExistsError,
    TeamMembershipNotFoundError,
    TeamMembershipOwnershipError,
    TeamNameAliasConflictError,
)

from ultrastats_ai.domain.team.membership import TeamMembership
from ultrastats_ai.domain.team.registration import SquadRegistration
from ultrastats_ai.domain.team.team import Team

__all__ = [
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
]