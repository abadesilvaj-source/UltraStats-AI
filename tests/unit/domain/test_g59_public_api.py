"""Contratos das APIs públicas concluídas na G5.9."""

import ultrastats_ai.domain.bankroll as bankroll_api
import ultrastats_ai.domain.betting as betting_api
import ultrastats_ai.domain.prediction as prediction_api
import ultrastats_ai.domain.recommendation as recommendation_api


def test_betting_public_api() -> None:
    assert set(betting_api.__all__) == {
        "BettingDomainError",
        "BettingMarket",
        "BettingSelection",
        "Bookmaker",
        "InvalidBettingEntityError",
        "OddsSnapshot",
    }


def test_prediction_public_api() -> None:
    assert set(prediction_api.__all__) == {
        "InvalidPredictionError",
        "Prediction",
        "PredictionDomainError",
        "PredictionExplanation",
        "PredictionResult",
    }


def test_recommendation_public_api() -> None:
    assert set(recommendation_api.__all__) == {
        "InvalidRecommendationError",
        "Recommendation",
    }


def test_bankroll_public_api() -> None:
    assert set(bankroll_api.__all__) == {
        "Bankroll",
        "BankrollDomainError",
        "BankrollTransaction",
        "Bet",
        "BetLeg",
        "InvalidBankrollOperationError",
        "Settlement",
        "SettlementResult",
        "TransactionType",
    }
