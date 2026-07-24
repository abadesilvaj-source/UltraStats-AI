"""API pública do Match Context."""

from ultrastats_ai.domain.match.enums import (
    MatchParticipantStatus,
    MatchType,
    SurfaceCondition,
    SurfaceType,
    VenueRole,
    VenueStatus,
    WeatherCondition,
)
from ultrastats_ai.domain.match.errors import (
    DuplicateMatchParticipantError,
    DuplicateMatchVenueError,
    DuplicateScheduleChangeError,
    InvalidMatchParticipantsError,
    InvalidMatchScheduleError,
    InvalidMatchStatusTransitionError,
    InvalidMatchVenueError,
    InvalidScheduleChangeError,
    MatchDomainError,
    MatchParticipantNotFoundError,
    MatchParticipantOwnershipError,
    MatchVenueOwnershipError,
    MultipleCurrentMatchVenuesError,
    ScheduleChangeOwnershipError,
)
from ultrastats_ai.domain.match.lifecycle import can_transition
from ultrastats_ai.domain.match.match import Match
from ultrastats_ai.domain.match.participant import MatchParticipant
from ultrastats_ai.domain.match.schedule_change import MatchScheduleChange
from ultrastats_ai.domain.match.venue import MatchVenue

__all__ = [
    "DuplicateMatchParticipantError",
    "DuplicateMatchVenueError",
    "DuplicateScheduleChangeError",
    "InvalidMatchParticipantsError",
    "InvalidMatchScheduleError",
    "InvalidMatchStatusTransitionError",
    "InvalidMatchVenueError",
    "InvalidScheduleChangeError",
    "Match",
    "MatchDomainError",
    "MatchParticipant",
    "MatchParticipantNotFoundError",
    "MatchParticipantOwnershipError",
    "MatchParticipantStatus",
    "MatchScheduleChange",
    "MatchType",
    "MatchVenue",
    "MatchVenueOwnershipError",
    "MultipleCurrentMatchVenuesError",
    "ScheduleChangeOwnershipError",
    "SurfaceCondition",
    "SurfaceType",
    "VenueRole",
    "VenueStatus",
    "WeatherCondition",
    "can_transition",
]
