from decimal import Decimal as D

import pytest

from ultrastats_ai.domain.policies import (
    AutoMatchThresholdPolicy,
    AwayGoalsPolicy,
    ConflictResolutionPolicy,
    DailyExposurePolicy,
    KellyFractionPolicy,
    ManualReviewThresholdPolicy,
    MatchWinnerPolicy,
    MaximumStakePolicy,
    MinimumConfidencePolicy,
    MinimumExpectedValuePolicy,
    ProviderPriorityPolicy,
)
from ultrastats_ai.domain.services import (
    BetSettlementService,
    DataFusionService,
    ExpectedValueCalculationService,
    FairOddCalculationService,
    IdentityResolutionService,
    MatchResultService,
    ProbabilityCalibrationService,
    RecommendationEvaluationService,
    StakeCalculationService,
    TieResolutionService,
)


def test_resolution_and_fusion_policies() -> None:
    priority = ProviderPriorityPolicy({"trusted": 1})
    assert priority.choose(("other", "trusted")) == "trusted"
    assert priority.choose(("z", "a")) == "a"
    with pytest.raises(ValueError):
        priority.choose(())
    fusion = DataFusionService(priority)
    assert fusion.fuse({"other": 1, "trusted": 2}) == 2
    conflict = ConflictResolutionPolicy(D("0.1"))
    assert conflict.resolve(D("1"), D("1.1")) == D("1")
    assert conflict.resolve(D("1"), D("1.2")) is None


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        ({}, ("unmatched", None)),
        ({"a": D("0.96")}, ("matched", "a")),
        ({"a": D("0.80")}, ("review", "a")),
        ({"a": D("0.20")}, ("unmatched", None)),
        ({"a": D("0.96"), "b": D("0.96")}, ("matched", "b")),
    ],
)
def test_identity_resolution(scores: dict[str, D], expected: tuple[str, str | None]) -> None:
    assert IdentityResolutionService().resolve(scores) == expected


def test_threshold_and_match_policies() -> None:
    assert AutoMatchThresholdPolicy().accepts(D(".95"))
    review = ManualReviewThresholdPolicy()
    assert review.requires_review(D(".70"))
    assert not review.requires_review(D(".96"))
    winner = MatchWinnerPolicy()
    assert [winner.winner(*score) for score in ((2, 1), (1, 2), (1, 1))] == [
        "home",
        "away",
        "draw",
    ]
    assert AwayGoalsPolicy().winner((2, 0), (1, 0)) == "home"
    assert AwayGoalsPolicy().winner((0, 2), (0, 1)) == "away"
    assert AwayGoalsPolicy().winner((1, 0), (1, 0)) is None
    assert AwayGoalsPolicy(True).winner((1, 0), (2, 1)) == "home"
    assert AwayGoalsPolicy(True).winner((3, 1), (2, 0)) == "away"


def test_financial_policies() -> None:
    assert MinimumExpectedValuePolicy(D(".05")).accepts(D(".05"))
    assert MinimumConfidencePolicy(D(".7")).accepts(D(".8"))
    assert MaximumStakePolicy(D(".1")).cap(D("100"), D("20")) == D("10")
    exposure = DailyExposurePolicy(D(".2"))
    assert exposure.available(D("100"), D("5")) == D("15")
    assert exposure.available(D("100"), D("25")) == 0
    kelly = KellyFractionPolicy(D(".25"))
    assert kelly.stake_fraction(D(".6"), D("2")) == D(".05")
    assert kelly.stake_fraction(D(".2"), D("2")) == 0
    with pytest.raises(ValueError):
        kelly.stake_fraction(D(".5"), D("1"))


def test_match_and_tie_services() -> None:
    service = MatchResultService()
    assert service.result(2, 1) == "home"
    assert service.result(1, 2) == "away"
    assert service.result(1, 1) == "draw"
    with pytest.raises(ValueError):
        service.result(-1, 0)
    tie = TieResolutionService()
    assert tie.resolve(3, 2) == "home"
    assert tie.resolve(2, 3) == "away"
    assert tie.resolve(2, 2) is None
    assert tie.resolve(2, 2, (5, 4)) == "home"
    assert tie.resolve(2, 2, (4, 5)) == "away"


def test_probability_odds_ev_and_recommendation_services() -> None:
    calibration = ProbabilityCalibrationService()
    assert calibration.normalize({"a": D("2"), "b": D("2")}) == {
        "a": D(".5"),
        "b": D(".5"),
    }
    for invalid in ({}, {"a": D("-1"), "b": D("2")}):
        with pytest.raises(ValueError):
            calibration.normalize(invalid)
    fair = FairOddCalculationService()
    assert fair.calculate(D(".5")) == 2
    for invalid in (D("0"), D("1.1")):
        with pytest.raises(ValueError):
            fair.calculate(invalid)
    assert ExpectedValueCalculationService().calculate(D(".6"), D("2")) == D(".2")
    recommendation = RecommendationEvaluationService(
        MinimumExpectedValuePolicy(D(".05")),
        MinimumConfidencePolicy(D(".7")),
    )
    assert recommendation.evaluate(D(".1"), D(".8"))
    assert not recommendation.evaluate(D("0"), D(".8"))
    assert not recommendation.evaluate(D(".1"), D(".6"))


def test_stake_and_settlement_services() -> None:
    stake = StakeCalculationService(
        KellyFractionPolicy(D(".25")),
        MaximumStakePolicy(D(".1")),
        DailyExposurePolicy(D(".2")),
    )
    assert stake.calculate(D("100"), D(".6"), D("2"), D("0")) == D("5")
    assert stake.calculate(D("100"), D(".9"), D("3"), D("19")) == D("1")
    settlement = BetSettlementService()
    assert settlement.return_amount(D("10"), D("2"), "won") == D("20")
    assert settlement.return_amount(D("10"), D("2"), "lost") == 0
    assert settlement.return_amount(D("10"), D("2"), "void") == D("10")
    assert settlement.return_amount(D("10"), D("2"), "half_won") == D("15")
    assert settlement.return_amount(D("10"), D("2"), "half_lost") == D("5")
    with pytest.raises(ValueError):
        settlement.return_amount(D("10"), D("2"), "cash_out")
