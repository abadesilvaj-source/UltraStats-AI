"""Estados profissionais canônicos de um jogador."""

from ultrastats_ai.domain.shared import DomainEnum


class PlayerStatus(DomainEnum):
    """Representa o estado profissional atual de um jogador."""

    YOUTH = "youth"
    AMATEUR = "amateur"
    PROFESSIONAL = "professional"
    FREE_AGENT = "free_agent"
    LOANED = "loaned"
    SUSPENDED = "suspended"
    INJURED = "injured"
    INACTIVE = "inactive"
    RETIRED = "retired"
    UNKNOWN = "unknown"