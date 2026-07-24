"""API pública do Recommendation Context."""

from ultrastats_ai.domain.recommendation.engine import (
    OddsQuote,
    Opportunity,
    OpportunityInput,
    OpportunityRisk,
    RecommendationEngine,
    RecommendationPolicy,
    compare_odds,
)
from ultrastats_ai.domain.recommendation.models import (
    InvalidRecommendationError,
    Recommendation,
)

__all__ = [
    "InvalidRecommendationError",
    "Recommendation",
]
