"""Classificação de risco."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class RiskClassification(DomainEnum):
    """Representa o nível de risco."""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"