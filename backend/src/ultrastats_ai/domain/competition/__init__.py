"""API pública do contexto de competições."""

from ultrastats_ai.domain.competition.aliases import (
    CompetitionAliases,
)
from ultrastats_ai.domain.competition.competition import (
    Competition,
)
from ultrastats_ai.domain.competition.errors import (
    AliasNotFoundError,
    CompetitionDomainError,
    CompetitionHierarchyError,
    DuplicateAliasError,
    DuplicateHistoryFieldError,
    DuplicateTieMatchError,
    DuplicateTieMatchSequenceError,
    EmptyHistoryChangesError,
    InvalidSeasonTransitionError,
    NameAliasConflictError,
)
from ultrastats_ai.domain.competition.history import (
    CompetitionChangeType,
    CompetitionEntityKind,
    CompetitionFieldChange,
    CompetitionHistoryEntry,
)
from ultrastats_ai.domain.competition.reconstruction import (
    CompetitionReconstruction,
    RoundReconstruction,
    SeasonReconstruction,
    StageReconstruction,
    TieReconstruction,
)
from ultrastats_ai.domain.competition.repositories import (
    CompetitionHistoryRepository,
    CompetitionRepository,
    SeasonRepository,
    TieRepository,
)
from ultrastats_ai.domain.competition.round import Round
from ultrastats_ai.domain.competition.season import Season
from ultrastats_ai.domain.competition.stage import Stage
from ultrastats_ai.domain.competition.tie import Tie
from ultrastats_ai.domain.competition.tie_match_reference import (
    TieMatchReference,
)

__all__ = [
    "AliasNotFoundError",
    "Competition",
    "CompetitionAliases",
    "CompetitionChangeType",
    "CompetitionDomainError",
    "CompetitionEntityKind",
    "CompetitionFieldChange",
    "CompetitionHierarchyError",
    "CompetitionHistoryEntry",
    "CompetitionHistoryRepository",
    "CompetitionReconstruction",
    "CompetitionRepository",
    "DuplicateAliasError",
    "DuplicateHistoryFieldError",
    "DuplicateTieMatchError",
    "DuplicateTieMatchSequenceError",
    "EmptyHistoryChangesError",
    "InvalidSeasonTransitionError",
    "NameAliasConflictError",
    "Round",
    "RoundReconstruction",
    "Season",
    "SeasonReconstruction",
    "SeasonRepository",
    "Stage",
    "StageReconstruction",
    "Tie",
    "TieMatchReference",
    "TieReconstruction",
    "TieRepository",
]