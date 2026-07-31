"""Modelos probabilísticos, ensemble, calibração e backtesting."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from math import exp, log
import random
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ModelSpecification:
    name: str
    version: str
    competition_id: str
    market: str
    parameters: Mapping[str, Decimal]

    def __post_init__(self) -> None:
        if not all((self.name.strip(), self.version.strip(), self.competition_id.strip(), self.market.strip())):
            raise ValueError("Modelo exige nome, versão, competição e mercado.")


@dataclass(frozen=True, slots=True)
class ProbabilisticForecast:
    model_name: str
    model_version: str
    market: str
    probabilities: Mapping[str, Decimal]
    explanations: Mapping[str, Decimal]

    def __post_init__(self) -> None:
        if not self.probabilities or any(value < 0 or value > 1 for value in self.probabilities.values()):
            raise ValueError("Probabilidades inválidas.")
        if abs(sum(self.probabilities.values(), Decimal("0")) - 1) > Decimal("0.000001"):
            raise ValueError("Probabilidades devem somar um.")


class PoissonScoreModel:
    def __init__(self, specification: ModelSpecification, *, max_goals: int = 10) -> None:
        if max_goals <= 0:
            raise ValueError("Limite de gols deve ser positivo.")
        self.specification, self.max_goals = specification, max_goals

    @staticmethod
    def count_distribution(expected: Decimal, maximum: int = 15) -> dict[int, Decimal]:
        if expected < 0 or maximum <= 0:
            raise ValueError("Parâmetros de distribuição inválidos.")
        values = {}
        probability = Decimal(str(exp(-float(expected))))
        values[0] = probability
        for count in range(1, maximum + 1):
            probability = probability * expected / count
            values[count] = probability
        total = sum(values.values(), Decimal("0"))
        return {key: value / total for key, value in values.items()}

    def scorelines(self, home_xg: Decimal, away_xg: Decimal) -> dict[tuple[int, int], Decimal]:
        home = self.count_distribution(home_xg, self.max_goals)
        away = self.count_distribution(away_xg, self.max_goals)
        return {
            (home_goals, away_goals): home_probability * away_probability
            for home_goals, home_probability in home.items()
            for away_goals, away_probability in away.items()
        }

    def predict(
        self,
        home_xg: Decimal,
        away_xg: Decimal,
        *,
        market: str | None = None,
        line: Decimal = Decimal("2.5"),
    ) -> ProbabilisticForecast:
        selected_market = market or self.specification.market
        scores = self.scorelines(home_xg, away_xg)
        probabilities = self._project(scores, selected_market, line, home_xg, away_xg)
        return ProbabilisticForecast(
            self.specification.name,
            self.specification.version,
            selected_market,
            probabilities,
            {"home_xg": home_xg, "away_xg": away_xg, "xg_difference": home_xg - away_xg},
        )

    @staticmethod
    def _project(scores, market, line, home_xg, away_xg):
        if market == "1x2":
            return _normalize(
                {
                    "home": sum(p for (h, a), p in scores.items() if h > a),
                    "draw": sum(p for (h, a), p in scores.items() if h == a),
                    "away": sum(p for (h, a), p in scores.items() if h < a),
                }
            )
        if market == "double_chance":
            base = PoissonScoreModel._project(scores, "1x2", line, home_xg, away_xg)
            return _normalize({"1x": base["home"] + base["draw"], "12": base["home"] + base["away"], "x2": base["draw"] + base["away"]})
        if market == "draw_no_bet":
            base = PoissonScoreModel._project(scores, "1x2", line, home_xg, away_xg)
            return _normalize({"home": base["home"], "away": base["away"]})
        if market in {"asian_handicap", "european_handicap"}:
            return _normalize(
                {
                    "home": sum(p for (h, a), p in scores.items() if Decimal(h - a) + line > 0),
                    "push": sum(p for (h, a), p in scores.items() if Decimal(h - a) + line == 0),
                    "away": sum(p for (h, a), p in scores.items() if Decimal(h - a) + line < 0),
                }
            )
        if market == "over_under":
            return _normalize(
                {
                    "over": sum(p for (h, a), p in scores.items() if Decimal(h + a) > line),
                    "under": sum(p for (h, a), p in scores.items() if Decimal(h + a) < line),
                }
            )
        if market == "both_teams_to_score":
            yes = sum(p for (h, a), p in scores.items() if h > 0 and a > 0)
            return _normalize({"yes": yes, "no": 1 - yes})
        if market in {"team_goals", "halftime"}:
            distribution = PoissonScoreModel.count_distribution(
                home_xg if market == "team_goals" else (home_xg + away_xg) / 2
            )
            over = sum(p for goals, p in distribution.items() if Decimal(goals) > line)
            return _normalize({"over": over, "under": 1 - over})
        if market in {"first_goal", "last_goal"}:
            total = home_xg + away_xg
            no_goal = Decimal(str(exp(-float(total))))
            if total == 0:
                return {"home": Decimal("0"), "away": Decimal("0"), "none": Decimal("1")}
            return _normalize({"home": (1 - no_goal) * home_xg / total, "away": (1 - no_goal) * away_xg / total, "none": no_goal})
        raise ValueError(f"Mercado de placar desconhecido: {market}.")


class CountMarketModel:
    def predict(self, expected: Decimal, line: Decimal, market: str) -> ProbabilisticForecast:
        distribution = PoissonScoreModel.count_distribution(expected)
        over = sum(value for count, value in distribution.items() if Decimal(count) > line)
        return ProbabilisticForecast("poisson_count", "1", market, _normalize({"over": over, "under": 1 - over}), {"expected": expected})


class EnsembleModel:
    def combine(
        self,
        forecasts: tuple[ProbabilisticForecast, ...],
        weights: tuple[Decimal, ...],
    ) -> ProbabilisticForecast:
        if not forecasts or len(forecasts) != len(weights) or any(weight <= 0 for weight in weights):
            raise ValueError("Ensemble exige forecasts e pesos positivos compatíveis.")
        if len({item.market for item in forecasts}) != 1:
            raise ValueError("Ensemble exige o mesmo mercado.")
        selections = set(forecasts[0].probabilities)
        if any(set(item.probabilities) != selections for item in forecasts):
            raise ValueError("Ensemble exige as mesmas seleções.")
        total = sum(weights, Decimal("0"))
        probabilities = {
            selection: sum(
                (forecast.probabilities[selection] * weight for forecast, weight in zip(forecasts, weights)),
                Decimal("0"),
            ) / total
            for selection in selections
        }
        return ProbabilisticForecast("ensemble", "1", forecasts[0].market, probabilities, {})


class ProbabilityCalibrator:
    def calibrate(self, forecast: ProbabilisticForecast, power: Decimal) -> ProbabilisticForecast:
        if power <= 0:
            raise ValueError("Potência de calibração deve ser positiva.")
        calibrated = _normalize({key: value**power for key, value in forecast.probabilities.items()})
        return ProbabilisticForecast(forecast.model_name, forecast.model_version, forecast.market, calibrated, forecast.explanations)


@dataclass(frozen=True, slots=True)
class BacktestResult:
    samples: int
    brier_score: Decimal
    log_loss: Decimal
    accuracy: Decimal
    calibration_error: Decimal


class Backtester:
    def evaluate(self, forecasts: tuple[ProbabilisticForecast, ...], outcomes: tuple[str, ...]) -> BacktestResult:
        if not forecasts or len(forecasts) != len(outcomes):
            raise ValueError("Backtest exige forecasts e outcomes compatíveis.")
        epsilon = Decimal("0.000000000001")
        brier = Decimal("0")
        loss = Decimal("0")
        correct = 0
        confidence_error = Decimal("0")
        for forecast, outcome in zip(forecasts, outcomes):
            if outcome not in forecast.probabilities:
                raise ValueError("Outcome ausente no forecast.")
            brier += sum(
                (probability - (1 if selection == outcome else 0)) ** 2
                for selection, probability in forecast.probabilities.items()
            )
            loss -= Decimal(str(log(float(max(epsilon, forecast.probabilities[outcome])))))
            predicted = max(forecast.probabilities, key=forecast.probabilities.get)
            correct += predicted == outcome
            confidence_error += abs(max(forecast.probabilities.values()) - (1 if predicted == outcome else 0))
        size = Decimal(len(forecasts))
        return BacktestResult(len(forecasts), brier / size, loss / size, Decimal(correct) / size, confidence_error / size)


class MonteCarloSimulator:
    def simulate(self, home_xg: Decimal, away_xg: Decimal, iterations: int, seed: int = 0) -> Mapping[str, Decimal]:
        if iterations <= 0:
            raise ValueError("Monte Carlo exige iterações.")
        randomizer = random.Random(seed)
        counts = {"home": 0, "draw": 0, "away": 0}
        for _ in range(iterations):
            home = _poisson_sample(float(home_xg), randomizer)
            away = _poisson_sample(float(away_xg), randomizer)
            counts["home" if home > away else "away" if away > home else "draw"] += 1
        return {key: Decimal(value) / iterations for key, value in counts.items()}


class RegimeChangeDetector:
    def detect(self, values: tuple[Decimal, ...], window: int, threshold: Decimal) -> bool:
        if window <= 0 or len(values) < window * 2 or threshold < 0:
            raise ValueError("Configuração de regime inválida.")
        previous = sum(values[-2 * window : -window], Decimal("0")) / window
        current = sum(values[-window:], Decimal("0")) / window
        return abs(current - previous) >= threshold


def conditional_probability(joint: Decimal, condition: Decimal) -> Decimal:
    if joint < 0 or condition <= 0 or joint > condition:
        raise ValueError("Probabilidade condicional inválida.")
    return joint / condition


def _normalize(values):
    total = sum(values.values(), Decimal("0"))
    if total <= 0:
        raise ValueError("Distribuição sem massa de probabilidade.")
    return {key: value / total for key, value in values.items()}


def _poisson_sample(rate: float, randomizer: random.Random) -> int:
    if rate == 0:
        return 0
    limit = exp(-rate)
    product, count = 1.0, 0
    while product > limit:
        count += 1
        product *= randomizer.random()
    return count - 1
