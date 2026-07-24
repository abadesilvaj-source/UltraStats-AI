"""Estados canônicos de participantes de partidas."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class MatchParticipantStatus(DomainEnum):
    """Representa a situação de uma equipe dentro de uma partida."""

    EXPECTED = "expected"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"
    DISQUALIFIED = "disqualified"
    REPLACED = "replaced"
    WALKOVER = "walkover"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    UNKNOWN = "unknown"
