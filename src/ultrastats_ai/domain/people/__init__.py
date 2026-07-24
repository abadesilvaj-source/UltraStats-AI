"""API pública do People Context."""

from ultrastats_ai.domain.people.aliases import PersonAliases
from ultrastats_ai.domain.people.coach import Coach
from ultrastats_ai.domain.people.enums import (
    CoachRole,
    CoachStatus,
    PeopleHistoryAction,
    PeopleProfileType,
    PlayerStatus,
    RefereeCategory,
    RefereeRole,
    RefereeStatus,
)

from ultrastats_ai.domain.people.history import (
    PersonHistoryEntry,
)

from ultrastats_ai.domain.people.errors import (
    DuplicatePersonAliasError,
    InvalidProfessionalPeriodError,
    InvalidRetirementStateError,
    PeopleDomainError,
    PersonAliasNotFoundError,
    PersonAlreadyActiveError,
    PersonAlreadyInactiveError,
    PersonNameAliasConflictError,
    PersonProfileAlreadyExistsError,
    PersonProfileNotFoundError,
    PersonProfileOwnershipError,
)
from ultrastats_ai.domain.people.person import Person
from ultrastats_ai.domain.people.player import Player
from ultrastats_ai.domain.people.referee import Referee

__all__ = [
    "Coach",
    "CoachRole",
    "CoachStatus",
    "DuplicatePersonAliasError",
    "InvalidProfessionalPeriodError",
    "InvalidRetirementStateError",
    "PeopleDomainError",
    "PeopleHistoryAction",
    "PeopleProfileType",
    "PersonHistoryEntry",
    "Person",
    "PersonAliasNotFoundError",
    "PersonAliases",
    "PersonAlreadyActiveError",
    "PersonAlreadyInactiveError",
    "PersonNameAliasConflictError",
    "PersonProfileAlreadyExistsError",
    "PersonProfileNotFoundError",
    "PersonProfileOwnershipError",
    "Player",
    "PlayerStatus",
    "Referee",
    "RefereeCategory",
    "RefereeRole",
    "RefereeStatus",
]