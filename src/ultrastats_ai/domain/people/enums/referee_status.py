"""Estados profissionais canônicos de árbitros."""

from ultrastats_ai.domain.shared import DomainEnum


class RefereeStatus(DomainEnum):
    """Representa a situação profissional atual de um árbitro."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
    RETIRED = "retired"
    UNKNOWN = "unknown"