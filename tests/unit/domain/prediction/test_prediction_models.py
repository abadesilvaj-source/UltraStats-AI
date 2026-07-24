"""Testes de Prediction e Recommendation."""

from dataclasses import replace

import pytest

from ultrastats_ai.domain.prediction import (
    InvalidPredictionError,
    Prediction,
    PredictionExplanation,
    PredictionResult,
)
from ultrastats_ai.domain.recommendation import (
    InvalidRecommendationError,
    Recommendation,
)
from ultrastats_ai.domain.shared import (
    BettingMarketId,
    BettingSelectionId,
    DecimalValue,
    MatchId,
    Odds,
    Percentage,
    PredictionExplanationId,
    PredictionId,
    PredictionModelId,
    PredictionResultId,
    PredictionStatus,
    Probability,
    RecommendationId,
    RecommendationStatus,
    RiskClassification,
    UtcTimestamp,
)


def result(prediction_id: PredictionId) -> PredictionResult:
    return PredictionResult(
        PredictionResultId.new(),
        prediction_id,
        BettingMarketId.new(),
        BettingSelectionId.new(),
        Probability("0.5"),
        Odds("2"),
    )


def explanation(
    prediction_id: PredictionId,
) -> PredictionExplanation:
    return PredictionExplanation(
        PredictionExplanationId.new(),
        prediction_id,
        "home_form",
        DecimalValue("0.12"),
        "Boa forma recente.",
    )


def prediction(
    *,
    status: PredictionStatus = PredictionStatus.PROCESSING,
) -> Prediction:
    return Prediction(
        PredictionId.new(),
        MatchId.new(),
        PredictionModelId.new(),
        "v1.0",
        status,
        UtcTimestamp("2026-08-01T10:00:00Z"),
    )


def test_prediction_builds_and_publishes_immutable_result() -> None:
    item = prediction()
    completed = (
        item.add_result(result(item.id))
        .add_explanation(explanation(item.id))
        .publish()
    )

    assert completed.status is PredictionStatus.COMPLETED
    assert len(completed.results) == 1
    with pytest.raises(InvalidPredictionError, match="imutável"):
        completed.add_result(result(completed.id))
    with pytest.raises(InvalidPredictionError, match="imutável"):
        completed.add_explanation(explanation(completed.id))


def test_completed_prediction_requires_result() -> None:
    with pytest.raises(InvalidPredictionError, match="resultados"):
        prediction(status=PredictionStatus.COMPLETED)


def test_prediction_requires_model_version() -> None:
    with pytest.raises(InvalidPredictionError, match="Versão"):
        replace(prediction(), model_version=" ")


def test_prediction_validates_owned_unique_records() -> None:
    item = prediction()
    owned = result(item.id)

    with pytest.raises(InvalidPredictionError, match="outra previsão"):
        replace(item, results=(result(PredictionId.new()),))
    with pytest.raises(InvalidPredictionError, match="duplicada"):
        replace(item, results=(owned, owned))
    with pytest.raises(TypeError, match="PredictionResult"):
        replace(item, results=(object(),))  # type: ignore[arg-type]


def test_prediction_result_validates_probability_and_fair_odds() -> None:
    item = result(PredictionId.new())

    with pytest.raises(InvalidPredictionError, match="positiva"):
        replace(item, probability=Probability(0))
    with pytest.raises(InvalidPredictionError, match="diverge"):
        replace(item, fair_odds=Odds("3"))


def test_explanation_requires_content() -> None:
    item = explanation(PredictionId.new())

    with pytest.raises(InvalidPredictionError, match="fator"):
        replace(item, factor="")


def test_prediction_type_validation() -> None:
    with pytest.raises(TypeError, match="id"):
        replace(prediction(), id=object())  # type: ignore[arg-type]


def test_recommendation_validates_expected_value() -> None:
    recommendation = Recommendation(
        RecommendationId.new(),
        PredictionId.new(),
        PredictionResultId.new(),
        BettingMarketId.new(),
        BettingSelectionId.new(),
        Odds("2"),
        Probability("0.6"),
        DecimalValue("0.2"),
        Probability("0.8"),
        Percentage("2"),
        RiskClassification.MEDIUM,
        RecommendationStatus.PUBLISHED,
        UtcTimestamp("2026-08-01T11:00:00Z"),
    )
    assert recommendation.expected_value.value > 0

    with pytest.raises(InvalidRecommendationError, match="diverge"):
        replace(
            recommendation,
            expected_value=DecimalValue("0.1"),
        )
    with pytest.raises(TypeError, match="id"):
        replace(recommendation, id=object())  # type: ignore[arg-type]
