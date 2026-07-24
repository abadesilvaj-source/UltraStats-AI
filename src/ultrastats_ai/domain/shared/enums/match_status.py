"""Estados canônicos de uma partida."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class MatchStatus(DomainEnum):
    """Representa o estado operacional de uma partida."""

    DATE_DEFINED = "date_defined"
    TIME_UNCONFIRMED = "time_unconfirmed"
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    PRE_MATCH = "pre_match"
    WARMUP = "warmup"
    FIRST_HALF = "first_half"
    SECOND_HALF = "second_half"
    POSTPONED = "postponed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    ABANDONED = "abandoned"
    LIVE = "live"
    HALF_TIME = "half_time"
    EXTRA_TIME = "extra_time"
    EXTRA_TIME_HALF_TIME = "extra_time_half_time"
    PENALTY_SHOOTOUT = "penalty_shootout"
    INTERRUPTED = "interrupted"
    SUSPENDED = "suspended"
    WALKOVER = "walkover"
    FINISHED = "finished"
    AFTER_EXTRA_TIME = "after_extra_time"
    AFTER_PENALTIES = "after_penalties"
    AWARDED = "awarded"
    UNKNOWN = "unknown"
