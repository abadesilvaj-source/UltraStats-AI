"""API pública do Match Context."""

from ultrastats_ai.domain.match.enums import (
    MatchParticipantStatus,
    MatchType,
)
from ultrastats_ai.domain.match.errors import (
    DuplicateMatchParticipantError,
    InvalidMatchParticipantsError,
    InvalidMatchScheduleError,
    MatchDomainError,
    MatchParticipantNotFoundError,
    MatchParticipantOwnershipError,
)
from ultrastats_ai.domain.match.match import Match
from ultrastats_ai.domain.match.participant import MatchParticipant

__all__ = [
    "DuplicateMatchParticipantError",
    "InvalidMatchParticipantsError",
    "InvalidMatchScheduleError",
    "Match",
    "MatchDomainError",
    "MatchParticipant",
    "MatchParticipantNotFoundError",
    "MatchParticipantOwnershipError",
    "MatchParticipantStatus",
    "MatchType",
]
