"""API pública do Recommendation Context."""

from ultrastats_ai.domain.recommendation.models import (
    InvalidRecommendationError,
    Recommendation,
)

__all__ = [
    "InvalidRecommendationError",
    "Recommendation",
]
