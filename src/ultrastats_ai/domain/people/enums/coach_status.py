"""Estados profissionais canônicos de treinadores."""

from ultrastats_ai.domain.shared import DomainEnum


class CoachStatus(DomainEnum):
    """Representa a situação profissional atual de um treinador."""

    ACTIVE = "active"
    UNEMPLOYED = "unemployed"
    SUSPENDED = "suspended"
    RETIRED = "retired"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"