"""Estados de uma recomendação."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class RecommendationStatus(DomainEnum):
    """Estado de uma recomendação."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"