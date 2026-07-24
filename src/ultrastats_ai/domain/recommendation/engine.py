"""Avaliação, segurança, ranking e diversificação de recomendações."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Mapping


class OpportunityRisk(StrEnum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    HIGH_RISK = "high_risk"
    SPECULATIVE = "speculative"


@dataclass(frozen=True, slots=True)
class OddsQuote:
    bookmaker: str
    odds: Decimal
    observed_at: datetime
    liquidity: Decimal = Decimal("1")
    available: bool = True

    def __post_init__(self) -> None:
        if not self.bookmaker.strip() or self.odds <= 1:
            raise ValueError("Cotação exige bookmaker e odd decimal válida.")
        if not Decimal("0") <= self.liquidity <= Decimal("1"):
            raise ValueError("Liquidez deve estar entre zero e um.")


@dataclass(frozen=True, slots=True)
class OpportunityInput:
    match_id: str
    market: str
    selection: str
    model_probability: Decimal
    model_confidence: Decimal
    sample_reliability: Decimal
    quotes: tuple[OddsQuote, ...]
    correlation_key: str

    def __post_init__(self) -> None:
        if not all((self.match_id.strip(), self.market.strip(), self.selection.strip(), self.correlation_key.strip())):
            raise ValueError("Oportunidade exige identidades e correlação.")
        if any(
            value < 0 or value > 1
            for value in (self.model_probability, self.model_confidence, self.sample_reliability)
        ):
            raise ValueError("Probabilidade, confiança e confiabilidade devem estar entre zero e um.")


@dataclass(frozen=True, slots=True)
class Opportunity:
    match_id: str
    market: str
    selection: str
    bookmaker: str | None
    offered_odds: Decimal | None
    implied_probability: Decimal | None
    model_probability: Decimal
    fair_odds: Decimal | None
    expected_value: Decimal | None
    edge: Decimal | None
    confidence: Decimal
    risk: OpportunityRisk
    score: Decimal
    safe: bool
    blocked_reasons: tuple[str, ...]
    explanation: tuple[str, ...]
    correlation_key: str
    evaluated_at: datetime


@dataclass(frozen=True, slots=True)
class RecommendationPolicy:
    minimum_ev: Decimal = Decimal("0.03")
    minimum_confidence: Decimal = Decimal("0.60")
    minimum_liquidity: Decimal = Decimal("0.30")
    maximum_odds: Decimal = Decimal("10")
    maximum_quote_age: timedelta = timedelta(minutes=15)

    def __post_init__(self) -> None:
        unit_interval = (
            self.minimum_ev,
            self.minimum_confidence,
            self.minimum_liquidity,
        )
        if any(value < 0 or value > 1 for value in unit_interval):
            raise ValueError("Limites de EV, confiança e liquidez devem estar entre zero e um.")
        if self.maximum_odds <= 1 or self.maximum_quote_age <= timedelta(0):
            raise ValueError("Odd máxima e idade máxima devem ser positivas.")


class RecommendationEngine:
    def __init__(self, policy: RecommendationPolicy = RecommendationPolicy()) -> None:
        self.policy = policy

    def evaluate(self, item: OpportunityInput, evaluated_at: datetime) -> Opportunity:
        valid_quotes = tuple(
            quote
            for quote in item.quotes
            if quote.available
            and quote.liquidity >= self.policy.minimum_liquidity
            and timedelta(0) <= evaluated_at - quote.observed_at <= self.policy.maximum_quote_age
        )
        best = max(valid_quotes, key=lambda quote: (quote.odds, quote.bookmaker)) if valid_quotes else None
        confidence = item.model_confidence * item.sample_reliability
        fair_odds = Decimal("1") / item.model_probability if item.model_probability > 0 else None
        implied = Decimal("1") / best.odds if best else None
        expected_value = item.model_probability * best.odds - 1 if best else None
        edge = item.model_probability - implied if implied is not None else None
        blocked = []
        if best is None:
            blocked.append("no_eligible_quote")
        elif best.odds > self.policy.maximum_odds:
            blocked.append("odds_above_safety_limit")
        if expected_value is None or expected_value < self.policy.minimum_ev:
            blocked.append("expected_value_below_minimum")
        if confidence < self.policy.minimum_confidence:
            blocked.append("confidence_below_minimum")
        risk = self._risk(best.odds if best else None, confidence)
        score = (
            max(Decimal("0"), expected_value or Decimal("0"))
            * confidence
            * (best.liquidity if best else Decimal("0"))
            / (Decimal("1") + (best.odds - 1 if best else Decimal("0")))
        )
        explanation = (
            f"model_probability={item.model_probability}",
            f"confidence={confidence}",
            f"expected_value={expected_value}",
            f"best_bookmaker={best.bookmaker if best else None}",
        )
        return Opportunity(
            item.match_id,
            item.market,
            item.selection,
            best.bookmaker if best else None,
            best.odds if best else None,
            implied,
            item.model_probability,
            fair_odds,
            expected_value,
            edge,
            confidence,
            risk,
            score,
            not blocked,
            tuple(blocked),
            explanation,
            item.correlation_key,
            evaluated_at,
        )

    @staticmethod
    def _risk(odds: Decimal | None, confidence: Decimal) -> OpportunityRisk:
        if odds is None or odds >= 8 or confidence < Decimal(".35"):
            return OpportunityRisk.SPECULATIVE
        if odds >= 5 or confidence < Decimal(".50"):
            return OpportunityRisk.HIGH_RISK
        if odds >= 3 or confidence < Decimal(".65"):
            return OpportunityRisk.AGGRESSIVE
        if odds >= 2 or confidence < Decimal(".80"):
            return OpportunityRisk.MODERATE
        return OpportunityRisk.CONSERVATIVE

    def rank(self, opportunities: tuple[Opportunity, ...]) -> tuple[Opportunity, ...]:
        return tuple(
            sorted(
                (item for item in opportunities if item.safe),
                key=lambda item: (-item.score, item.match_id, item.market, item.selection),
            )
        )

    def portfolio(
        self,
        opportunities: tuple[Opportunity, ...],
        *,
        maximum: int,
        maximum_per_correlation: int = 1,
    ) -> tuple[Opportunity, ...]:
        if maximum <= 0 or maximum_per_correlation <= 0:
            raise ValueError("Limites do portfólio devem ser positivos.")
        selected = []
        counts: dict[str, int] = {}
        for item in self.rank(opportunities):
            if counts.get(item.correlation_key, 0) >= maximum_per_correlation:
                continue
            selected.append(item)
            counts[item.correlation_key] = counts.get(item.correlation_key, 0) + 1
            if len(selected) == maximum:
                break
        return tuple(selected)


def compare_odds(quotes: tuple[OddsQuote, ...]) -> tuple[OddsQuote, ...]:
    return tuple(sorted((quote for quote in quotes if quote.available), key=lambda quote: (-quote.odds, quote.bookmaker)))
