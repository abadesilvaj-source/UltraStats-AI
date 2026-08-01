"""Estados de uma previsão."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class PredictionStatus(DomainEnum):
    """Estado de uma previsão."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FAILED = "failed"