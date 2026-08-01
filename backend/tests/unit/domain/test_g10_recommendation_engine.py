from datetime import datetime, timedelta, timezone
from decimal import Decimal as D

import pytest

from ultrastats_ai.domain.recommendation import (
    OddsQuote,
    OpportunityInput,
    OpportunityRisk,
    RecommendationEngine,
    RecommendationPolicy,
    compare_odds,
)


NOW = datetime.now(timezone.utc)


def quote(bookmaker="book", odds=D("2"), *, age=0, liquidity=D("1"), available=True):
    return OddsQuote(
        bookmaker,
        odds,
        NOW - timedelta(minutes=age),
        liquidity,
        available,
    )


def item(quotes, probability=D(".6"), confidence=D(".9"), reliability=D(".9"), correlation="match"):
    return OpportunityInput(
        "match",
        "1x2",
        "home",
        probability,
        confidence,
        reliability,
        quotes,
        correlation,
    )


def test_quote_input_and_policy_validation() -> None:
    with pytest.raises(ValueError, match="Cotação"):
        quote("", D("2"))
    with pytest.raises(ValueError, match="Cotação"):
        quote("book", D("1"))
    with pytest.raises(ValueError, match="Liquidez"):
        quote(liquidity=D("1.1"))
    with pytest.raises(ValueError, match="identidades"):
        OpportunityInput("", "m", "s", D(".5"), D(".5"), D(".5"), (), "c")
    with pytest.raises(ValueError, match="entre zero"):
        item((), probability=D("1.1"))
    with pytest.raises(ValueError, match="Limites"):
        RecommendationPolicy(minimum_ev=D("1.1"))
    with pytest.raises(ValueError, match="Odd máxima"):
        RecommendationPolicy(maximum_odds=D("1"))


def test_safe_evaluation_best_odds_metrics_and_explanation() -> None:
    engine = RecommendationEngine()
    opportunity = engine.evaluate(
        item((quote("a", D("2")), quote("b", D("2.2")))),
        NOW,
    )
    assert opportunity.safe
    assert opportunity.bookmaker == "b"
    assert opportunity.offered_odds == D("2.2")
    assert opportunity.implied_probability == D("1") / D("2.2")
    assert opportunity.fair_odds == D("1") / D(".6")
    assert opportunity.expected_value == D(".32")
    assert opportunity.edge > 0 and opportunity.score > 0
    assert opportunity.risk is OpportunityRisk.MODERATE
    assert "best_bookmaker=b" in opportunity.explanation


def test_security_filters_no_quote_stale_liquidity_odds_ev_and_confidence() -> None:
    engine = RecommendationEngine()
    blocked = engine.evaluate(
        item(
            (
                quote("stale", D("3"), age=20),
                OddsQuote("future", D("3"), NOW + timedelta(minutes=1)),
                quote("dry", D("3"), liquidity=D(".1")),
                quote("off", D("3"), available=False),
            ),
            probability=D("0"),
            confidence=D(".2"),
            reliability=D(".5"),
        ),
        NOW,
    )
    assert not blocked.safe
    assert blocked.bookmaker is None
    assert blocked.fair_odds is None
    assert blocked.risk is OpportunityRisk.SPECULATIVE
    assert set(blocked.blocked_reasons) == {
        "no_eligible_quote",
        "expected_value_below_minimum",
        "confidence_below_minimum",
    }
    high = engine.evaluate(item((quote(odds=D("12")),)), NOW)
    assert "odds_above_safety_limit" in high.blocked_reasons
    low_ev = engine.evaluate(item((quote(odds=D("1.5")),), probability=D(".5")), NOW)
    assert "expected_value_below_minimum" in low_ev.blocked_reasons
    low_confidence = engine.evaluate(
        item((quote(),), confidence=D(".5"), reliability=D(".5")), NOW
    )
    assert "confidence_below_minimum" in low_confidence.blocked_reasons


@pytest.mark.parametrize(
    ("odds", "confidence", "risk"),
    [
        (None, D("1"), OpportunityRisk.SPECULATIVE),
        (D("8"), D("1"), OpportunityRisk.SPECULATIVE),
        (D("2"), D(".3"), OpportunityRisk.SPECULATIVE),
        (D("5"), D("1"), OpportunityRisk.HIGH_RISK),
        (D("2"), D(".4"), OpportunityRisk.HIGH_RISK),
        (D("3"), D("1"), OpportunityRisk.AGGRESSIVE),
        (D("2"), D(".6"), OpportunityRisk.AGGRESSIVE),
        (D("2"), D("1"), OpportunityRisk.MODERATE),
        (D("1.8"), D(".7"), OpportunityRisk.MODERATE),
        (D("1.8"), D(".9"), OpportunityRisk.CONSERVATIVE),
    ],
)
def test_risk_classification(odds, confidence, risk) -> None:
    assert RecommendationEngine._risk(odds, confidence) is risk


def test_ranking_portfolio_correlation_and_odds_comparison() -> None:
    engine = RecommendationEngine(RecommendationPolicy(minimum_ev=D("0")))
    first = engine.evaluate(item((quote("a", D("2.2")),), correlation="same"), NOW)
    second = engine.evaluate(
        OpportunityInput("match2", "btts", "yes", D(".7"), D(".9"), D(".9"), (quote("b", D("2")),), "same"),
        NOW,
    )
    third = engine.evaluate(
        OpportunityInput("match3", "total", "over", D(".7"), D(".9"), D(".9"), (quote("c", D("2")),), "other"),
        NOW,
    )
    unsafe = RecommendationEngine().evaluate(item((), correlation="unsafe"), NOW)
    ranked = engine.rank((first, second, third, unsafe))
    assert unsafe not in ranked
    portfolio = engine.portfolio((first, second, third), maximum=2)
    assert len(portfolio) == 2
    assert len({value.correlation_key for value in portfolio}) == 2
    assert len(engine.portfolio((first, second), maximum=2, maximum_per_correlation=2)) == 2
    with pytest.raises(ValueError, match="Limites"):
        engine.portfolio((first,), maximum=0)
    compared = compare_odds((quote("a", D("2")), quote("b", D("3")), quote("x", D("4"), available=False)))
    assert [value.bookmaker for value in compared] == ["b", "a"]
