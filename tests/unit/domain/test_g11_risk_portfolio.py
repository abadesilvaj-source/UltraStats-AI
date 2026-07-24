from decimal import Decimal as D

import pytest

from ultrastats_ai.domain.risk import (
    BetCandidate,
    ExposureState,
    RiskPortfolioEngine,
    RiskProfile,
    RiskProfileKind,
    full_kelly,
    performance_metrics,
)


def candidate(
    identifier="a",
    *,
    competition="league",
    market="1x2",
    correlation="match",
    probability=D(".6"),
    odds=D("2"),
    score=D(".5"),
):
    return BetCandidate(
        identifier,
        competition,
        market,
        correlation,
        probability,
        odds,
        score,
    )


@pytest.mark.parametrize(
    ("kind", "kelly", "stake", "daily", "correlated"),
    [
        (RiskProfileKind.CONSERVATIVE, D(".25"), D(".01"), D(".05"), 1),
        (RiskProfileKind.MODERATE, D(".50"), D(".02"), D(".10"), 1),
        (RiskProfileKind.AGGRESSIVE, D(".75"), D(".03"), D(".15"), 2),
    ],
)
def test_profile_presets(kind, kelly, stake, daily, correlated) -> None:
    profile = RiskProfile.preset(kind)
    assert profile.kelly_fraction == kelly
    assert profile.maximum_stake_fraction == stake
    assert profile.maximum_daily_fraction == daily
    assert profile.maximum_correlated_positions == correlated


def test_profile_and_candidate_validation() -> None:
    with pytest.raises(ValueError, match="Frações"):
        RiskProfile(RiskProfileKind.MODERATE, D("0"), D(".1"), D(".1"), D(".1"), D(".1"))
    with pytest.raises(ValueError, match="correlação"):
        RiskProfile(
            RiskProfileKind.MODERATE,
            D(".5"),
            D(".1"),
            D(".1"),
            D(".1"),
            D(".1"),
            0,
        )
    with pytest.raises(ValueError, match="identidades"):
        candidate("")
    with pytest.raises(ValueError, match="inválidas"):
        candidate(probability=D("0"))
    with pytest.raises(ValueError, match="Score"):
        candidate(score=D("-.1"))


def test_exposure_validation() -> None:
    with pytest.raises(ValueError, match="negativas"):
        ExposureState(daily=D("-1"))
    with pytest.raises(ValueError, match="negativas"):
        ExposureState(by_competition={"a": D("-1")})
    with pytest.raises(ValueError, match="correlação"):
        ExposureState(by_correlation={"a": -1})


def test_full_kelly() -> None:
    assert full_kelly(D(".6"), D("2")) == D(".2")
    assert full_kelly(D(".4"), D("2")) == 0
    with pytest.raises(ValueError, match="Kelly"):
        full_kelly(D("1.1"), D("2"))
    with pytest.raises(ValueError, match="Kelly"):
        full_kelly(D(".5"), D("1"))


def test_portfolio_optimization_ranks_and_caps_stake() -> None:
    profile = RiskProfile.preset(RiskProfileKind.MODERATE)
    plan = RiskPortfolioEngine(profile).optimize(
        D("1000"),
        (
            candidate("low", correlation="low", score=D(".1")),
            candidate("high", correlation="high", score=D(".9")),
        ),
    )
    assert [item.recommendation_id for item in plan.positions] == ["high", "low"]
    assert all(item.stake == D("20") for item in plan.positions)
    assert plan.total_exposure == D("40")
    assert not plan.blocked


def test_portfolio_blocks_non_positive_kelly_and_correlation() -> None:
    engine = RiskPortfolioEngine(RiskProfile.preset(RiskProfileKind.CONSERVATIVE))
    plan = engine.optimize(
        D("1000"),
        (
            candidate("first", score=D(".9")),
            candidate("correlated", score=D(".8")),
            candidate("negative", correlation="other", probability=D(".4"), score=D(".7")),
        ),
    )
    assert [item.recommendation_id for item in plan.positions] == ["first"]
    assert plan.blocked["correlated"] == ("correlation_limit",)
    assert plan.blocked["negative"] == ("non_positive_kelly", "exposure_limit")


@pytest.mark.parametrize(
    "exposure",
    [
        ExposureState(daily=D("50")),
        ExposureState(by_competition={"league": D("30")}),
        ExposureState(by_market={"1x2": D("25")}),
    ],
)
def test_portfolio_blocks_exhausted_exposure_limits(exposure) -> None:
    plan = RiskPortfolioEngine(RiskProfile.preset(RiskProfileKind.CONSERVATIVE)).optimize(
        D("1000"), (candidate(),), exposure
    )
    assert plan.blocked["a"] == ("exposure_limit",)


def test_portfolio_accounts_for_existing_exposure_and_validates_bankroll() -> None:
    profile = RiskProfile.preset(RiskProfileKind.MODERATE)
    exposure = ExposureState(
        daily=D("10"),
        by_competition={"league": D("5")},
        by_market={"1x2": D("5")},
        by_correlation={"existing": 1},
    )
    plan = RiskPortfolioEngine(profile).optimize(
        D("1000"),
        (candidate("new", correlation="new"), candidate("blocked", correlation="existing")),
        exposure,
    )
    assert plan.positions[0].stake == D("20")
    assert plan.blocked["blocked"] == ("correlation_limit",)
    with pytest.raises(ValueError, match="Banca"):
        RiskPortfolioEngine(profile).optimize(D("0"), ())


def test_performance_metrics_roi_yield_and_drawdown() -> None:
    metrics = performance_metrics(
        D("100"),
        (D("10"), D("10"), D("10")),
        (D("10"), D("-20"), D("5")),
    )
    assert metrics.total_staked == D("30")
    assert metrics.net_profit == D("-5")
    assert metrics.roi == D("-.05")
    assert metrics.yield_rate == D("-5") / D("30")
    assert metrics.maximum_drawdown == D("20") / D("110")
    empty = performance_metrics(D("100"), (), ())
    assert empty.yield_rate == 0
    with pytest.raises(ValueError, match="Desempenho"):
        performance_metrics(D("0"), (), ())
    with pytest.raises(ValueError, match="equivalentes"):
        performance_metrics(D("100"), (D("1"),), ())
    with pytest.raises(ValueError, match="Stakes"):
        performance_metrics(D("100"), (D("-1"),), (D("0"),))


def test_strategy_simulator_compounds_and_tracks_curve() -> None:
    engine = RiskPortfolioEngine(RiskProfile.preset(RiskProfileKind.MODERATE))
    result = engine.simulate(
        D("1000"),
        ((D(".6"), D("2"), True), (D(".6"), D("2"), False)),
    )
    assert result.equity_curve == (D("1000"), D("1020"), D("999.60"))
    assert result.final_bankroll == D("999.60")
    assert result.metrics.total_staked == D("40.40")
    with pytest.raises(ValueError, match="inicial"):
        engine.simulate(D("0"), ())
