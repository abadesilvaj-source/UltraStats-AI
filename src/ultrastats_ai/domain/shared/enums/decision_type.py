"""Tipos canônicos de decisões esportivas e administrativas."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class DecisionType(DomainEnum):
    """Representa a natureza de uma decisão do domínio esportivo."""

    CONFIRMED = "confirmed"
    OVERTURNED = "overturned"
    AWARDED = "awarded"
    DISALLOWED = "disallowed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    POSTPONED = "postponed"
    ABANDONED = "abandoned"
    RESCHEDULED = "rescheduled"
    ADMINISTRATIVE_WIN = "administrative_win"
    ADMINISTRATIVE_DRAW = "administrative_draw"
    POINTS_DEDUCTION = "points_deduction"
    FINE = "fine"
    NO_ACTION = "no_action"