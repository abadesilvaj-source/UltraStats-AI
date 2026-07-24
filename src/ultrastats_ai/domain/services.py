"""Domain Services que coordenam cálculos e decisões entre agregados."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping

from ultrastats_ai.domain.policies import (
    DailyExposurePolicy,
    KellyFractionPolicy,
    MaximumStakePolicy,
    MinimumConfidencePolicy,
    MinimumExpectedValuePolicy,
    ProviderPriorityPolicy,
)


@dataclass(frozen=True, slots=True)
class IdentityResolutionService:
    auto_threshold: Decimal = Decimal("0.95")
    review_threshold: Decimal = Decimal("0.70")

    def resolve(self, scores: Mapping[str, Decimal]) -> tuple[str, str | None]:
        if not scores:
            return ("unmatched", None)
        candidate, score = max(scores.items(), key=lambda item: (item[1], item[0]))
        state = "matched" if score >= self.auto_threshold else "review" if score >= self.review_threshold else "unmatched"
        return (state, candidate if state != "unmatched" else None)


@dataclass(frozen=True, slots=True)
class DataFusionService:
    provider_policy: ProviderPriorityPolicy

    def fuse(self, observations: Mapping[str, object]) -> object:
        provider = self.provider_policy.choose(tuple(observations))
        return observations[provider]


class MatchResultService:
    def result(self, home_score: int, away_score: int) -> str:
        if min(home_score, away_score) < 0:
            raise ValueError("Placar não pode ser negativo.")
        return "home" if home_score > away_score else "away" if away_score > home_score else "draw"


class TieResolutionService:
    def resolve(self, home_total: int, away_total: int, shootout: tuple[int, int] | None = None) -> str | None:
        if home_total != away_total:
            return "home" if home_total > away_total else "away"
        if shootout and shootout[0] != shootout[1]:
            return "home" if shootout[0] > shootout[1] else "away"
        return None


class ProbabilityCalibrationService:
    def normalize(self, probabilities: Mapping[str, Decimal]) -> dict[str, Decimal]:
        total = sum(probabilities.values(), Decimal("0"))
        if total <= 0 or any(value < 0 for value in probabilities.values()):
            raise ValueError("Probabilidades devem ser não negativas e possuir soma positiva.")
        return {key: value / total for key, value in probabilities.items()}


class FairOddCalculationService:
    def calculate(self, probability: Decimal) -> Decimal:
        if not Decimal("0") < probability <= Decimal("1"):
            raise ValueError("Probabilidade deve estar no intervalo (0, 1].")
        return Decimal("1") / probability


class ExpectedValueCalculationService:
    def calculate(self, probability: Decimal, decimal_odds: Decimal) -> Decimal:
        return probability * decimal_odds - Decimal("1")


@dataclass(frozen=True, slots=True)
class RecommendationEvaluationService:
    ev_policy: MinimumExpectedValuePolicy
    confidence_policy: MinimumConfidencePolicy

    def evaluate(self, expected_value: Decimal, confidence: Decimal) -> bool:
        return self.ev_policy.accepts(expected_value) and self.confidence_policy.accepts(confidence)


@dataclass(frozen=True, slots=True)
class StakeCalculationService:
    kelly: KellyFractionPolicy
    maximum: MaximumStakePolicy
    exposure: DailyExposurePolicy

    def calculate(
        self,
        bankroll: Decimal,
        probability: Decimal,
        decimal_odds: Decimal,
        current_exposure: Decimal,
    ) -> Decimal:
        proposed = bankroll * self.kelly.stake_fraction(probability, decimal_odds)
        return min(
            self.maximum.cap(bankroll, proposed),
            self.exposure.available(bankroll, current_exposure),
        )


class BetSettlementService:
    def return_amount(self, stake: Decimal, decimal_odds: Decimal, result: str) -> Decimal:
        factors = {
            "won": decimal_odds,
            "lost": Decimal("0"),
            "void": Decimal("1"),
            "half_won": (decimal_odds + 1) / 2,
            "half_lost": Decimal("0.5"),
        }
        if result not in factors:
            raise ValueError("Resultado de liquidação desconhecido.")
        return stake * factors[result]
