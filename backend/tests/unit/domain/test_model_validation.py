from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ultrastats_ai.domain.model_validation import (
    BacktestEngine,
    BacktestMetrics,
    CalibrationModel,
    ForecastSample,
    ModelGate,
    TemporalDatasetBuilder,
    TrainingExample,
)


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def example(index: int) -> TrainingExample:
    return TrainingExample(
        f"m{index}",
        NOW + timedelta(days=index),
        {"form": Decimal(index) / 10},
        "home" if index % 2 else "away",
        frozenset({"api_football", "football_data"}),
    )


def forecast(index: int, *, odds: bool = True) -> ForecastSample:
    home = Decimal("0.7") if index % 2 else Decimal("0.2")
    away = Decimal("0.2") if index % 2 else Decimal("0.7")
    return ForecastSample(
        f"m{index}",
        {"home": home, "draw": Decimal("0.1"), "away": away},
        "home" if index % 2 else "away",
        {"home": Decimal("2"), "draw": Decimal("3"), "away": Decimal("2")} if odds else None,
    )


def test_training_example_and_temporal_splits() -> None:
    with pytest.raises(ValueError):
        TrainingExample("", NOW, {}, "", frozenset())
    examples = tuple(example(index) for index in reversed(range(10)))
    split = TemporalDatasetBuilder().split(examples)
    assert len(split.training) == 6
    assert split.training[0].match_id == "m0"
    windows = TemporalDatasetBuilder().rolling_windows(
        examples, minimum_training=4, horizon=2
    )
    assert len(windows) == 3 and len(windows[0].test) == 2


@pytest.mark.parametrize(
    "operation",
    [
        lambda builder: builder.split(()),
        lambda builder: builder.split(
            tuple(example(i) for i in range(5)),
            validation_fraction=Decimal("0.6"),
            test_fraction=Decimal("0.4"),
        ),
        lambda builder: builder.split(
            tuple(example(i) for i in range(2)),
            validation_fraction=Decimal("0.2"),
            test_fraction=Decimal("0.2"),
        ),
        lambda builder: builder.rolling_windows(
            tuple(example(i) for i in range(5)), minimum_training=0, horizon=1
        ),
    ],
)
def test_dataset_builder_rejects_invalid_configuration(operation) -> None:
    with pytest.raises(ValueError):
        operation(TemporalDatasetBuilder())


def test_backtest_metrics_calibration_roi_and_gate() -> None:
    samples = tuple(forecast(index) for index in range(10))
    metrics = BacktestEngine().evaluate(samples, bins=5)
    assert metrics.samples == 10
    assert metrics.accuracy == 1
    assert metrics.roi == 1
    assert metrics.brier_score < Decimal("0.2")
    gate = ModelGate(
        Decimal("0.3"),
        Decimal("0.5"),
        Decimal("0.3"),
        Decimal("0.8"),
        10,
    )
    assert gate.evaluate(metrics) == (True, ())
    failed = BacktestMetrics(1, Decimal("1"), Decimal("2"), Decimal("0"), Decimal("1"), None)
    approved, reasons = gate.evaluate(failed)
    assert not approved and len(reasons) == 5


def test_backtest_without_odds_and_validation_errors() -> None:
    metrics = BacktestEngine().evaluate(tuple(forecast(i, odds=False) for i in range(2)))
    assert metrics.roi is None
    with pytest.raises(ValueError):
        BacktestEngine().evaluate(())
    with pytest.raises(ValueError):
        BacktestEngine().evaluate((forecast(1),), bins=0)
    with pytest.raises(ValueError):
        BacktestEngine().evaluate(
            (
                forecast(1),
                ForecastSample("x", {"yes": Decimal("0.5"), "no": Decimal("0.5")}, "yes"),
            )
        )
    with pytest.raises(ValueError):
        ForecastSample("x", {"home": Decimal("0.8"), "away": Decimal("0.8")}, "home")
    with pytest.raises(ValueError):
        ForecastSample("x", {"home": Decimal("1"), "away": Decimal("0")}, "home")


def test_temperature_calibration() -> None:
    model = CalibrationModel(Decimal("2"))
    calibrated = model.calibrate({"home": Decimal("0.8"), "away": Decimal("0.2")})
    assert sum(calibrated.values(), Decimal("0")) == Decimal("1")
    assert calibrated["home"] < Decimal("0.8")
    with pytest.raises(ValueError):
        CalibrationModel(Decimal("0")).calibrate({"home": Decimal("1")})
    with pytest.raises(ValueError):
        model.calibrate({})
