"""Estados institucionais de uma equipe."""

from ultrastats_ai.domain.shared import DomainEnum


class TeamStatus(DomainEnum):
    """Representa o estado institucional atual da equipe."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DISSOLVED = "dissolved"
    UNKNOWN = "unknown"