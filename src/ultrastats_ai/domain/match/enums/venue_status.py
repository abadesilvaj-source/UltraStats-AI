"""Estado de um local no contexto de uma partida."""

from ultrastats_ai.domain.shared.enums import DomainEnum


class VenueStatus(DomainEnum):
    """Representa a situação operacional ou histórica do local."""

    PLANNED = "planned"
    PROVISIONAL = "provisional"
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    CHANGED = "changed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"
