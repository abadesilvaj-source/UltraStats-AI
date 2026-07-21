"""Estados de uma aposta."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class BetStatus(DomainEnum):
    """Estado de uma aposta."""

    OPEN = "open"
    WON = "won"
    LOST = "lost"
    VOID = "void"
    HALF_WON = "half_won"
    HALF_LOST = "half_lost"
    CASH_OUT = "cash_out"
    CANCELLED = "cancelled"
    PENDING = "pending"