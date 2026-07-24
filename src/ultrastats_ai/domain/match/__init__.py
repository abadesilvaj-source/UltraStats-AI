"""API pública do Match Context."""

from ultrastats_ai.domain.match.enums import (
    MatchParticipantStatus,
    MatchType,
)
from ultrastats_ai.domain.match.errors import (
    DuplicateMatchParticipantError,
    DuplicateScheduleChangeError,
    InvalidMatchParticipantsError,
    InvalidMatchScheduleError,
    InvalidMatchStatusTransitionError,
    InvalidScheduleChangeError,
    MatchDomainError,
    MatchParticipantNotFoundError,
    MatchParticipantOwnershipError,
    ScheduleChangeOwnershipError,
)
from ultrastats_ai.domain.match.lifecycle import can_transition
from ultrastats_ai.domain.match.match import Match
from ultrastats_ai.domain.match.participant import MatchParticipant
from ultrastats_ai.domain.match.schedule_change import MatchScheduleChange

__all__ = [
    "DuplicateMatchParticipantError",
    "DuplicateScheduleChangeError",
    "InvalidMatchParticipantsError",
    "InvalidMatchScheduleError",
    "InvalidMatchStatusTransitionError",
    "InvalidScheduleChangeError",
    "Match",
    "MatchDomainError",
    "MatchParticipant",
    "MatchParticipantNotFoundError",
    "MatchParticipantOwnershipError",
    "MatchParticipantStatus",
    "MatchScheduleChange",
    "MatchType",
    "ScheduleChangeOwnershipError",
    "can_transition",
]
