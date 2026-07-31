"""Estados canônicos de uma temporada."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class SeasonStatus(DomainEnum):
    """Representa o estado atual de uma temporada."""

    PLANNED = "planned"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    CANCELLED = "cancelled"