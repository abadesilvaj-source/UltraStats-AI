"""Estados canônicos de uma partida."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class MatchStatus(DomainEnum):
    """Representa o estado operacional de uma partida."""

    SCHEDULED = "scheduled"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"
    ABANDONED = "abandoned"
    LIVE = "live"
    HALF_TIME = "half_time"
    EXTRA_TIME = "extra_time"
    PENALTY_SHOOTOUT = "penalty_shootout"
    FINISHED = "finished"
    AWARDED = "awarded"