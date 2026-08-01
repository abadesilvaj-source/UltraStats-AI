"""Estados de inscrição esportiva em elenco."""

from ultrastats_ai.domain.shared import DomainEnum


class SquadRegistrationStatus(DomainEnum):
    """Representa o estado de uma inscrição em elenco."""

    PENDING = "pending"
    REGISTERED = "registered"
    SUSPENDED = "suspended"
    INELIGIBLE = "ineligible"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    UNKNOWN = "unknown"