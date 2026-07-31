from decimal import Decimal as D

import pytest

from ultrastats_ai.domain.prediction import engine as prediction_engine
from ultrastats_ai.domain.prediction import (
    Backtester,
    CountMarketModel,
    EnsembleModel,
    ModelSpecification,
    MonteCarloSimulator,
    PoissonScoreModel,
    ProbabilisticForecast,
    ProbabilityCalibrator,
    RegimeChangeDetector,
    conditional_probability,
)


def specification(market="1x2"):
    return ModelSpecification("poisson", "1.0", "league", market, {"decay": D(".9")})


def test_specification_forecast_and_model_validation() -> None:
    with pytest.raises(ValueError, match="Modelo"):
        ModelSpecification("", "1", "league", "1x2", {})
    with pytest.raises(ValueError, match="Limite"):
        PoissonScoreModel(specification(), max_goals=0)
    with pytest.raises(ValueError, match="Probabilidades"):
        ProbabilisticForecast("m", "1", "x", {}, {})
    with pytest.raises(ValueError, match="somar"):
        ProbabilisticForecast("m", "1", "x", {"a": D(".2")}, {})
    with pytest.raises(ValueError, match="Probabilidades"):
        ProbabilisticForecast("m", "1", "x", {"a": D("1.1"), "b": D("-.1")}, {})
    with pytest.raises(ValueError, match="massa"):
        prediction_engine._normalize({"empty": D("0")})


def test_poisson_score_markets_and_explanations() -> None:
    model = PoissonScoreModel(specification(), max_goals=8)
    for market, selections in (
        ("1x2", {"home", "draw", "away"}),
        ("double_chance", {"1x", "12", "x2"}),
        ("draw_no_bet", {"home", "away"}),
        ("asian_handicap", {"home", "push", "away"}),
        ("european_handicap", {"home", "push", "away"}),
        ("over_under", {"over", "under"}),
        ("both_teams_to_score", {"yes", "no"}),
        ("team_goals", {"over", "under"}),
        ("halftime", {"over", "under"}),
        ("first_goal", {"home", "away", "none"}),
        ("last_goal", {"home", "away", "none"}),
    ):
        forecast = model.predict(D("1.6"), D("1.1"), market=market)
        assert set(forecast.probabilities) == selections
        assert sum(forecast.probabilities.values()) == 1
        assert forecast.explanations["xg_difference"] == D(".5")
    assert model.predict(D("1"), D("1")).market == "1x2"
    assert model.predict(D("0"), D("0"), market="first_goal").probabilities["none"] == 1
    with pytest.raises(ValueError, match="desconhecido"):
        model.predict(D("1"), D("1"), market="corners")


def test_count_distribution_and_count_markets() -> None:
    distribution = PoissonScoreModel.count_distribution(D("2"), 5)
    assert sum(distribution.values()) == 1
    with pytest.raises(ValueError, match="distribuição"):
        PoissonScoreModel.count_distribution(D("-1"))
    with pytest.raises(ValueError, match="distribuição"):
        PoissonScoreModel.count_distribution(D("1"), 0)
    model = CountMarketModel()
    for market in ("corners", "cards", "player_markets", "match_statistics"):
        assert model.predict(D("4"), D("3.5"), market).market == market


def test_ensemble_and_calibration() -> None:
    first = ProbabilisticForecast("a", "1", "1x2", {"h": D(".6"), "a": D(".4")}, {})
    second = ProbabilisticForecast("b", "1", "1x2", {"h": D(".4"), "a": D(".6")}, {})
    combined = EnsembleModel().combine((first, second), (D("2"), D("1")))
    assert combined.probabilities["h"] > combined.probabilities["a"]
    for forecasts, weights in (((), ()), ((first,), ()), ((first,), (D("0"),))):
        with pytest.raises(ValueError, match="pesos"):
            EnsembleModel().combine(forecasts, weights)
    other_market = ProbabilisticForecast("c", "1", "other", {"h": D(".6"), "a": D(".4")}, {})
    with pytest.raises(ValueError, match="mercado"):
        EnsembleModel().combine((first, other_market), (D("1"), D("1")))
    other_selections = ProbabilisticForecast("c", "1", "1x2", {"x": D(".6"), "a": D(".4")}, {})
    with pytest.raises(ValueError, match="seleções"):
        EnsembleModel().combine((first, other_selections), (D("1"), D("1")))
    calibrated = ProbabilityCalibrator().calibrate(first, D("2"))
    assert calibrated.probabilities["h"] > first.probabilities["h"]
    with pytest.raises(ValueError, match="Potência"):
        ProbabilityCalibrator().calibrate(first, D("0"))


def test_backtesting_metrics_and_errors() -> None:
    forecasts = (
        ProbabilisticForecast("m", "1", "1x2", {"h": D(".8"), "a": D(".2")}, {}),
        ProbabilisticForecast("m", "1", "1x2", {"h": D(".3"), "a": D(".7")}, {}),
    )
    result = Backtester().evaluate(forecasts, ("h", "h"))
    assert result.samples == 2
    assert result.accuracy == D(".5")
    assert result.brier_score > 0 and result.log_loss > 0
    with pytest.raises(ValueError, match="compatíveis"):
        Backtester().evaluate((), ())
    with pytest.raises(ValueError, match="Outcome"):
        Backtester().evaluate((forecasts[0],), ("draw",))
    zero = ProbabilisticForecast("m", "1", "x", {"h": D("0"), "a": D("1")}, {})
    assert Backtester().evaluate((zero,), ("h",)).log_loss > 1


def test_monte_carlo_conditional_and_regime_change() -> None:
    simulation = MonteCarloSimulator().simulate(D("1.5"), D("1"), 500, seed=7)
    assert sum(simulation.values()) == 1
    zero = MonteCarloSimulator().simulate(D("0"), D("0"), 10)
    assert zero["draw"] == 1
    with pytest.raises(ValueError, match="iterações"):
        MonteCarloSimulator().simulate(D("1"), D("1"), 0)
    detector = RegimeChangeDetector()
    assert detector.detect((D("1"), D("1"), D("3"), D("3")), 2, D("1"))
    assert not detector.detect((D("1"), D("1"), D("1.1"), D("1.1")), 2, D("1"))
    for values, window, threshold in (((D("1"),), 1, D("1")), ((D("1"), D("2")), 0, D("1")), ((D("1"), D("2")), 1, D("-1"))):
        with pytest.raises(ValueError, match="regime"):
            detector.detect(values, window, threshold)
    assert conditional_probability(D(".2"), D(".5")) == D(".4")
    for joint, condition in ((D("-1"), D(".5")), (D(".2"), D("0")), (D(".8"), D(".5"))):
        with pytest.raises(ValueError, match="condicional"):
            conditional_probability(joint, condition)
