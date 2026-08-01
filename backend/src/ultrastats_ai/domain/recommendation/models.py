"""Recomendação auditável derivada de uma previsão."""

from dataclasses import dataclass
from decimal import Decimal

from ultrastats_ai.domain.shared import (
    BettingMarketId,
    BettingSelectionId,
    DecimalValue,
    Odds,
    Percentage,
    PredictionId,
    PredictionResultId,
    Probability,
    RecommendationId,
    RecommendationStatus,
    RiskClassification,
    UtcTimestamp,
)
from ultrastats_ai.domain.shared.errors import DomainError


class InvalidRecommendationError(DomainError):
    """Indica uma recomendação incoerente."""


@dataclass(frozen=True, slots=True)
class Recommendation:
    id: RecommendationId
    prediction_id: PredictionId
    result_id: PredictionResultId
    market_id: BettingMarketId
    selection_id: BettingSelectionId
    offered_odds: Odds
    probability: Probability
    expected_value: DecimalValue
    confidence: Probability
    suggested_stake_percent: Percentage
    risk: RiskClassification
    status: RecommendationStatus
    created_at: UtcTimestamp

    def __post_init__(self) -> None:
        fields = (
            (self.id, RecommendationId, "id"),
            (self.prediction_id, PredictionId, "prediction_id"),
            (self.result_id, PredictionResultId, "result_id"),
            (self.market_id, BettingMarketId, "market_id"),
            (self.selection_id, BettingSelectionId, "selection_id"),
            (self.offered_odds, Odds, "offered_odds"),
            (self.probability, Probability, "probability"),
            (self.expected_value, DecimalValue, "expected_value"),
            (self.confidence, Probability, "confidence"),
            (
                self.suggested_stake_percent,
                Percentage,
                "suggested_stake_percent",
            ),
            (self.risk, RiskClassification, "risk"),
            (self.status, RecommendationStatus, "status"),
            (self.created_at, UtcTimestamp, "created_at"),
        )
        for value, expected, name in fields:
            if not isinstance(value, expected):
                raise TypeError(f"{name} deve ser {expected.__name__}.")
        calculated = (
            self.probability.value * self.offered_odds.value
            - Decimal("1")
        )
        if abs(self.expected_value.value - calculated) > Decimal("0.0001"):
            raise InvalidRecommendationError(
                "Valor esperado diverge da probabilidade e da odd."
            )
