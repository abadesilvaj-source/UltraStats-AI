"""Motor estatístico canônico, temporal e determinístico."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from math import exp
from typing import Mapping


@dataclass(frozen=True, slots=True)
class MatchSample:
    match_id: str
    team_id: str
    competition_id: str
    occurred_at: datetime
    is_home: bool
    goals_for: Decimal
    goals_against: Decimal
    expected_goals_for: Decimal
    expected_goals_against: Decimal
    opponent_strength: Decimal
    points: Decimal
    coach_id: str | None = None
    referee_id: str | None = None
    absence_impact: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        numeric = (
            self.goals_for,
            self.goals_against,
            self.expected_goals_for,
            self.expected_goals_against,
            self.opponent_strength,
            self.points,
            self.absence_impact,
        )
        if not self.match_id.strip() or not self.team_id.strip() or not self.competition_id.strip():
            raise ValueError("Amostra exige identidades.")
        if any(value < 0 for value in numeric):
            raise ValueError("Métricas da amostra não podem ser negativas.")
        if self.points not in {Decimal("0"), Decimal("1"), Decimal("3")}:
            raise ValueError("Pontos devem representar derrota, empate ou vitória.")


@dataclass(frozen=True, slots=True)
class Distribution:
    mean: Decimal
    variance: Decimal
    minimum: Decimal
    maximum: Decimal


@dataclass(frozen=True, slots=True)
class StatisticalSnapshot:
    team_id: str
    reference_at: datetime
    sample_size: int
    effective_sample_size: Decimal
    reliability: Decimal
    metrics: Mapping[str, Decimal]
    distributions: Mapping[str, Distribution]
    trends: Mapping[str, Decimal]
    contexts: Mapping[str, Decimal]


class StatisticalEngine:
    def __init__(self, *, decay: Decimal = Decimal("0.90"), target_sample: int = 10) -> None:
        if not Decimal("0") < decay <= Decimal("1") or target_sample <= 0:
            raise ValueError("Configuração estatística inválida.")
        self.decay, self.target_sample = decay, target_sample

    def calculate(
        self,
        team_id: str,
        samples: tuple[MatchSample, ...],
        reference_at: datetime,
    ) -> StatisticalSnapshot:
        eligible = tuple(
            sorted(
                (
                    item
                    for item in samples
                    if item.team_id == team_id and item.occurred_at < reference_at
                ),
                key=lambda item: item.occurred_at,
                reverse=True,
            )
        )
        if not eligible:
            raise ValueError("Não existem amostras anteriores ao instante de referência.")
        weights = tuple(self.decay**index for index in range(len(eligible)))
        metrics = {
            "recent_form": self._mean(tuple(item.points for item in eligible), weights) / 3,
            "goals_for": self._mean(tuple(item.goals_for for item in eligible), weights),
            "goals_against": self._mean(tuple(item.goals_against for item in eligible), weights),
            "expected_goals_for": self._mean(
                tuple(item.expected_goals_for for item in eligible), weights
            ),
            "expected_goals_against": self._mean(
                tuple(item.expected_goals_against for item in eligible), weights
            ),
            "schedule_strength": self._mean(
                tuple(item.opponent_strength for item in eligible), weights
            ),
            "absence_impact": self._mean(
                tuple(item.absence_impact for item in eligible), weights
            ),
        }
        for label, home in (("home", True), ("away", False)):
            subset = tuple(item for item in eligible if item.is_home is home)
            metrics[f"{label}_performance"] = (
                sum((item.points for item in subset), Decimal("0"))
                / (Decimal(3) * len(subset))
                if subset
                else Decimal("0")
            )
        goals = tuple(item.goals_for for item in eligible)
        xg = tuple(item.expected_goals_for for item in eligible)
        distributions = {
            "goals_for": self._distribution(goals, weights),
            "expected_goals_for": self._distribution(xg, weights),
        }
        trends = {
            "goals_for": self._trend(goals),
            "expected_goals_for": self._trend(xg),
            "form": self._trend(tuple(item.points for item in eligible)),
        }
        latest = eligible[0]
        contexts = {
            "competition_form": self._context(eligible, "competition_id", latest.competition_id),
            "coach_form": self._context(eligible, "coach_id", latest.coach_id),
            "referee_points": self._context(eligible, "referee_id", latest.referee_id),
        }
        effective = self._effective_sample_size(weights)
        reliability = min(Decimal("1"), effective / self.target_sample)
        return StatisticalSnapshot(
            team_id,
            reference_at,
            len(eligible),
            effective,
            reliability,
            metrics,
            distributions,
            trends,
            contexts,
        )

    @staticmethod
    def poisson_probability(expected_goals: Decimal, goals: int) -> Decimal:
        if expected_goals < 0 or goals < 0:
            raise ValueError("Parâmetros de Poisson não podem ser negativos.")
        factorial = 1
        for value in range(2, goals + 1):
            factorial *= value
        power = Decimal("1") if goals == 0 else expected_goals**goals
        return Decimal(str(exp(-float(expected_goals)))) * power / factorial

    @staticmethod
    def _mean(values: tuple[Decimal, ...], weights: tuple[Decimal, ...]) -> Decimal:
        total = sum(weights, Decimal("0"))
        return sum((value * weight for value, weight in zip(values, weights)), Decimal("0")) / total

    @classmethod
    def _distribution(
        cls, values: tuple[Decimal, ...], weights: tuple[Decimal, ...]
    ) -> Distribution:
        mean = cls._mean(values, weights)
        variance = cls._mean(tuple((value - mean) ** 2 for value in values), weights)
        return Distribution(mean, variance, min(values), max(values))

    @staticmethod
    def _trend(values: tuple[Decimal, ...]) -> Decimal:
        if len(values) < 2:
            return Decimal("0")
        chronological = tuple(reversed(values))
        return (chronological[-1] - chronological[0]) / (len(values) - 1)

    @staticmethod
    def _effective_sample_size(weights: tuple[Decimal, ...]) -> Decimal:
        total = sum(weights, Decimal("0"))
        return total**2 / sum((weight**2 for weight in weights), Decimal("0"))

    @staticmethod
    def _context(samples: tuple[MatchSample, ...], field: str, value: str | None) -> Decimal:
        if value is None:
            return Decimal("0")
        selected = tuple(item for item in samples if getattr(item, field) == value)
        return sum((item.points for item in selected), Decimal("0")) / (Decimal(3) * len(selected))
