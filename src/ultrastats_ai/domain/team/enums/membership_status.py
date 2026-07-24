"""Estados de um vínculo entre pessoa e equipe."""

from ultrastats_ai.domain.shared import DomainEnum


class MembershipStatus(DomainEnum):
    """Representa o estado atual de um vínculo com a equipe."""

    PLANNED = "planned"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ENDED = "ended"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"