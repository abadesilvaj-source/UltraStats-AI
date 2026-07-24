"""Papel de um local no contexto de uma partida."""

from ultrastats_ai.domain.shared.enums import DomainEnum


class VenueRole(DomainEnum):
    """Classifica a função histórica ou operacional do local."""

    PRIMARY = "primary"
    ALTERNATIVE = "alternative"
    TEMPORARY = "temporary"
    TRAINING = "training"
    EMERGENCY = "emergency"
    BACKUP = "backup"
    ORIGINAL = "original"
    FINAL = "final"
    OTHER = "other"
    UNKNOWN = "unknown"
