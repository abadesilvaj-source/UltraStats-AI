"""Previsões imutáveis, resultados e explicações."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal

from ultrastats_ai.domain.shared import (
    BettingMarketId,
    BettingSelectionId,
    DecimalValue,
    MatchId,
    Odds,
    PredictionExplanationId,
    PredictionId,
    PredictionModelId,
    PredictionResultId,
    PredictionStatus,
    Probability,
    UtcTimestamp,
)
from ultrastats_ai.domain.shared.errors import DomainError


class PredictionDomainError(DomainError):
    """Erro-base do Prediction Context."""


class InvalidPredictionError(PredictionDomainError):
    """Indica uma previsão inconsistente."""


@dataclass(frozen=True, slots=True)
class PredictionResult:
    id: PredictionResultId
    prediction_id: PredictionId
    market_id: BettingMarketId
    selection_id: BettingSelectionId
    probability: Probability
    fair_odds: Odds

    def __post_init__(self) -> None:
        _types(
            (self.id, PredictionResultId, "id"),
            (self.prediction_id, PredictionId, "prediction_id"),
            (self.market_id, BettingMarketId, "market_id"),
            (self.selection_id, BettingSelectionId, "selection_id"),
            (self.probability, Probability, "probability"),
            (self.fair_odds, Odds, "fair_odds"),
        )
        if self.probability.value == 0:
            raise InvalidPredictionError(
                "Resultado preditivo exige probabilidade positiva."
            )
        expected = Decimal("1") / self.probability.value
        if abs(self.fair_odds.value - expected) > Decimal("0.0001"):
            raise InvalidPredictionError(
                "Odd justa diverge da probabilidade."
            )


@dataclass(frozen=True, slots=True)
class PredictionExplanation:
    id: PredictionExplanationId
    prediction_id: PredictionId
    factor: str
    impact: DecimalValue
    narrative: str

    def __post_init__(self) -> None:
        _types(
            (self.id, PredictionExplanationId, "id"),
            (self.prediction_id, PredictionId, "prediction_id"),
            (self.factor, str, "factor"),
            (self.impact, DecimalValue, "impact"),
            (self.narrative, str, "narrative"),
        )
        if not self.factor.strip() or not self.narrative.strip():
            raise InvalidPredictionError(
                "Explicação exige fator e narrativa."
            )


@dataclass(frozen=True, slots=True)
class Prediction:
    id: PredictionId
    match_id: MatchId
    model_id: PredictionModelId
    model_version: str
    status: PredictionStatus
    generated_at: UtcTimestamp
    results: tuple[PredictionResult, ...] = ()
    explanations: tuple[PredictionExplanation, ...] = ()

    def __post_init__(self) -> None:
        _types(
            (self.id, PredictionId, "id"),
            (self.match_id, MatchId, "match_id"),
            (self.model_id, PredictionModelId, "model_id"),
            (self.model_version, str, "model_version"),
            (self.status, PredictionStatus, "status"),
            (self.generated_at, UtcTimestamp, "generated_at"),
            (self.results, tuple, "results"),
            (self.explanations, tuple, "explanations"),
        )
        if not self.model_version.strip():
            raise InvalidPredictionError("Versão do modelo é obrigatória.")
        _owned_unique(self.results, PredictionResult, self.id)
        _owned_unique(self.explanations, PredictionExplanation, self.id)
        if self.status is PredictionStatus.COMPLETED and not self.results:
            raise InvalidPredictionError(
                "Previsão concluída exige resultados."
            )

    def add_result(self, result: PredictionResult) -> Prediction:
        if self.status is PredictionStatus.COMPLETED:
            raise InvalidPredictionError(
                "Previsão publicada é imutável."
            )
        return replace(self, results=(*self.results, result))

    def add_explanation(
        self,
        explanation: PredictionExplanation,
    ) -> Prediction:
        if self.status is PredictionStatus.COMPLETED:
            raise InvalidPredictionError(
                "Previsão publicada é imutável."
            )
        return replace(
            self,
            explanations=(*self.explanations, explanation),
        )

    def publish(self) -> Prediction:
        return replace(self, status=PredictionStatus.COMPLETED)


def _types(*items: tuple[object, type, str]) -> None:
    for value, expected, field in items:
        if not isinstance(value, expected):
            raise TypeError(f"{field} deve ser {expected.__name__}.")


def _owned_unique(
    items: tuple[object, ...],
    expected: type,
    prediction_id: PredictionId,
) -> None:
    ids: set[object] = set()
    for item in items:
        _types((item, expected, expected.__name__))
        if item.prediction_id != prediction_id:
            raise InvalidPredictionError(
                f"{expected.__name__} pertence a outra previsão."
            )
        if item.id in ids:
            raise InvalidPredictionError(
                f"{expected.__name__} possui identidade duplicada."
            )
        ids.add(item.id)
