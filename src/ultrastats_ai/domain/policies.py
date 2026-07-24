"""Políticas determinísticas compartilhadas pelos contextos canônicos."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ProviderPriorityPolicy:
    priorities: Mapping[str, int]

    def choose(self, providers: tuple[str, ...]) -> str:
        if not providers:
            raise ValueError("Ao menos um provider é obrigatório.")
        return min(providers, key=lambda item: (self.priorities.get(item, 10_000), item))


@dataclass(frozen=True, slots=True)
class ConflictResolutionPolicy:
    tolerance: Decimal

    def resolve(self, preferred: Decimal, alternative: Decimal) -> Decimal | None:
        return preferred if abs(preferred - alternative) <= self.tolerance else None


@dataclass(frozen=True, slots=True)
class AutoMatchThresholdPolicy:
    threshold: Decimal = Decimal("0.95")

    def accepts(self, score: Decimal) -> bool:
        return score >= self.threshold


@dataclass(frozen=True, slots=True)
class ManualReviewThresholdPolicy:
    threshold: Decimal = Decimal("0.70")

    def requires_review(self, score: Decimal, auto_threshold: Decimal = Decimal("0.95")) -> bool:
        return self.threshold <= score < auto_threshold


class MatchWinnerPolicy:
    def winner(self, home_score: int, away_score: int) -> str:
        return "home" if home_score > away_score else "away" if away_score > home_score else "draw"


@dataclass(frozen=True, slots=True)
class AwayGoalsPolicy:
    enabled: bool = False

    def winner(self, first_leg: tuple[int, int], second_leg: tuple[int, int]) -> str | None:
        home_total = first_leg[0] + second_leg[1]
        away_total = first_leg[1] + second_leg[0]
        if home_total != away_total:
            return "home" if home_total > away_total else "away"
        if self.enabled and first_leg[1] != second_leg[1]:
            return "home" if second_leg[1] > first_leg[1] else "away"
        return None


@dataclass(frozen=True, slots=True)
class MinimumExpectedValuePolicy:
    minimum: Decimal

    def accepts(self, expected_value: Decimal) -> bool:
        return expected_value >= self.minimum


@dataclass(frozen=True, slots=True)
class MinimumConfidencePolicy:
    minimum: Decimal

    def accepts(self, confidence: Decimal) -> bool:
        return confidence >= self.minimum


@dataclass(frozen=True, slots=True)
class MaximumStakePolicy:
    fraction: Decimal

    def cap(self, bankroll: Decimal, proposed: Decimal) -> Decimal:
        return min(proposed, bankroll * self.fraction)


@dataclass(frozen=True, slots=True)
class DailyExposurePolicy:
    fraction: Decimal

    def available(self, bankroll: Decimal, current_exposure: Decimal) -> Decimal:
        return max(Decimal("0"), bankroll * self.fraction - current_exposure)


@dataclass(frozen=True, slots=True)
class KellyFractionPolicy:
    fraction: Decimal = Decimal("0.25")

    def stake_fraction(self, probability: Decimal, decimal_odds: Decimal) -> Decimal:
        if decimal_odds <= 1:
            raise ValueError("Odd decimal deve ser maior que 1.")
        full_kelly = (probability * decimal_odds - 1) / (decimal_odds - 1)
        return max(Decimal("0"), full_kelly * self.fraction)
