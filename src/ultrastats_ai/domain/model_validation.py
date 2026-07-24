"""Dataset temporal, backtesting, calibração e aprovação de modelos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from math import log
from typing import Mapping


@dataclass(frozen=True, slots=True)
class TrainingExample:
    match_id: str
    occurred_at: datetime
    features: Mapping[str, Decimal]
    outcome: str
    provider_coverage: frozenset[str]

    def __post_init__(self) -> None:
        if not self.match_id.strip() or not self.outcome.strip() or not self.features:
            raise ValueError("Exemplo de treinamento inválido.")


@dataclass(frozen=True, slots=True)
class DatasetSplit:
    training: tuple[TrainingExample, ...]
    validation: tuple[TrainingExample, ...]
    test: tuple[TrainingExample, ...]


class TemporalDatasetBuilder:
    def split(
        self,
        examples: tuple[TrainingExample, ...],
        *,
        validation_fraction: Decimal = Decimal("0.2"),
        test_fraction: Decimal = Decimal("0.2"),
    ) -> DatasetSplit:
        if not examples or validation_fraction <= 0 or test_fraction <= 0:
            raise ValueError("Dataset e frações devem ser positivos.")
        if validation_fraction + test_fraction >= 1:
            raise ValueError("Treino deve possuir uma fração positiva.")
        ordered = tuple(sorted(examples, key=lambda item: (item.occurred_at, item.match_id)))
        size = len(ordered)
        validation_size = max(1, int(size * validation_fraction))
        test_size = max(1, int(size * test_fraction))
        training_end = size - validation_size - test_size
        if training_end < 1:
            raise ValueError("Dataset insuficiente para três partições.")
        return DatasetSplit(
            ordered[:training_end],
            ordered[training_end : training_end + validation_size],
            ordered[training_end + validation_size :],
        )

    def rolling_windows(
        self,
        examples: tuple[TrainingExample, ...],
        *,
        minimum_training: int,
        horizon: int,
    ) -> tuple[DatasetSplit, ...]:
        if minimum_training <= 0 or horizon <= 0:
            raise ValueError("Janela temporal inválida.")
        ordered = tuple(sorted(examples, key=lambda item: (item.occurred_at, item.match_id)))
        windows = []
        cursor = minimum_training
        while cursor + horizon <= len(ordered):
            windows.append(
                DatasetSplit(
                    ordered[:cursor],
                    (),
                    ordered[cursor : cursor + horizon],
                )
            )
            cursor += horizon
        return tuple(windows)


@dataclass(frozen=True, slots=True)
class ForecastSample:
    match_id: str
    probabilities: Mapping[str, Decimal]
    outcome: str
    offered_odds: Mapping[str, Decimal] | None = None

    def __post_init__(self) -> None:
        total = sum(self.probabilities.values(), Decimal("0"))
        if self.outcome not in self.probabilities or any(
            value <= 0 or value >= 1 for value in self.probabilities.values()
        ):
            raise ValueError("Previsão de backtest inválida.")
        if abs(total - Decimal("1")) > Decimal("0.0001"):
            raise ValueError("Probabilidades devem somar um.")


@dataclass(frozen=True, slots=True)
class BacktestMetrics:
    samples: int
    brier_score: Decimal
    log_loss: Decimal
    accuracy: Decimal
    calibration_error: Decimal
    roi: Decimal | None


class BacktestEngine:
    def evaluate(self, samples: tuple[ForecastSample, ...], *, bins: int = 10) -> BacktestMetrics:
        if not samples or bins <= 0:
            raise ValueError("Backtest exige amostras e bins.")
        labels = tuple(sorted(samples[0].probabilities))
        if any(tuple(sorted(sample.probabilities)) != labels for sample in samples):
            raise ValueError("Mercados incompatíveis no backtest.")
        count = Decimal(len(samples))
        brier = sum(
            (
                sum(
                    (
                        (probability - (Decimal("1") if label == sample.outcome else Decimal("0")))
                        ** 2
                        for label, probability in sample.probabilities.items()
                    ),
                    Decimal("0"),
                )
                for sample in samples
            ),
            Decimal("0"),
        ) / count
        loss = sum(
            (Decimal(str(-log(float(sample.probabilities[sample.outcome])))) for sample in samples),
            Decimal("0"),
        ) / count
        accuracy = (
            sum(
                1
                for sample in samples
                if max(sample.probabilities, key=sample.probabilities.get) == sample.outcome
            )
            / len(samples)
        )
        calibration = self._calibration_error(samples, bins)
        bets = [
            (sample, max(sample.probabilities, key=sample.probabilities.get))
            for sample in samples
            if sample.offered_odds
        ]
        profit = Decimal("0")
        for sample, selection in bets:
            odds = sample.offered_odds
            assert odds is not None
            if selection in odds:
                profit += odds[selection] - 1 if selection == sample.outcome else Decimal("-1")
        roi = profit / len(bets) if bets else None
        return BacktestMetrics(
            len(samples),
            brier,
            loss,
            Decimal(str(accuracy)),
            calibration,
            roi,
        )

    @staticmethod
    def _calibration_error(samples: tuple[ForecastSample, ...], bins: int) -> Decimal:
        points = [
            (probability, Decimal("1") if label == sample.outcome else Decimal("0"))
            for sample in samples
            for label, probability in sample.probabilities.items()
        ]
        error = Decimal("0")
        for index in range(bins):
            lower, upper = Decimal(index) / bins, Decimal(index + 1) / bins
            bucket = [
                item
                for item in points
                if lower <= item[0] < upper or (index == bins - 1 and item[0] == upper)
            ]
            if bucket:
                confidence = sum((item[0] for item in bucket), Decimal("0")) / len(bucket)
                frequency = sum((item[1] for item in bucket), Decimal("0")) / len(bucket)
                error += abs(confidence - frequency) * Decimal(len(bucket)) / len(points)
        return error


@dataclass(frozen=True, slots=True)
class CalibrationModel:
    temperature: Decimal

    def calibrate(self, probabilities: Mapping[str, Decimal]) -> Mapping[str, Decimal]:
        if self.temperature <= 0 or not probabilities:
            raise ValueError("Calibração inválida.")
        powered = {
            label: Decimal(str(float(value) ** (1 / float(self.temperature))))
            for label, value in probabilities.items()
        }
        total = sum(powered.values(), Decimal("0"))
        return {label: value / total for label, value in powered.items()}


@dataclass(frozen=True, slots=True)
class ModelGate:
    maximum_brier: Decimal
    maximum_log_loss: Decimal
    maximum_calibration_error: Decimal
    minimum_accuracy: Decimal
    minimum_samples: int

    def evaluate(self, metrics: BacktestMetrics) -> tuple[bool, tuple[str, ...]]:
        failures = []
        checks = (
            (metrics.samples < self.minimum_samples, "insufficient_samples"),
            (metrics.brier_score > self.maximum_brier, "brier_score"),
            (metrics.log_loss > self.maximum_log_loss, "log_loss"),
            (metrics.calibration_error > self.maximum_calibration_error, "calibration_error"),
            (metrics.accuracy < self.minimum_accuracy, "accuracy"),
        )
        failures.extend(name for failed, name in checks if failed)
        return not failures, tuple(failures)
