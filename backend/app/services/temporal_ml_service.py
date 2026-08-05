from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timezone
from hashlib import sha256
from math import exp, log, sqrt
import os
from statistics import mean, pstdev

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.models import Match, MatchStatistics
from ultrastats_ai.infrastructure.database.models import PredictiveModelRecord


MARKETS = {
    "match_winner": ("Home", "Draw", "Away"),
    "over_2_5_goals": ("Under 2.5", "Over 2.5"),
    "both_teams_to_score": ("No", "Yes"),
}
MODEL_NAME = "temporal_logistic"
MODEL_VERSION = "temporal-logit-v1"
MINIMUM_SAMPLES = 300
MAXIMUM_SAMPLES = 5_000
TRAINING_EPOCHS = 100


class TemporalMLService:
    """Modelo supervisionado leve com corte temporal e calibração holdout.

    O treinador usa somente partidas anteriores à observação, separa treino,
    calibração e teste em ordem cronológica e persiste coeficientes reproduzíveis.
    Se a amostra ou as tabelas canônicas não estiverem disponíveis, o pipeline
    simplesmente mantém o baseline estatístico existente.
    """

    def __init__(
        self,
        session: Session,
        *,
        allow_training: bool = True,
        force_retraining: bool = False,
    ) -> None:
        self.session = session
        self.allow_training = allow_training
        self.force_retraining = force_retraining
        self._models: dict[str, dict[str, object]] | None = None

    def predict(self, match: Match) -> dict[str, dict[str, float]]:
        models = self._load_or_train()
        features = self._features_for_match(match)
        if features is None:
            return {}
        result: dict[str, dict[str, float]] = {}
        for market, labels in MARKETS.items():
            parameters = models.get(market)
            if not parameters or not bool(parameters.get("approved")):
                continue
            probabilities = self._infer(features, parameters)
            result[market] = dict(zip(labels, probabilities))
        return result

    def _load_or_train(self) -> dict[str, dict[str, object]]:
        if self._models is not None:
            return self._models
        if not inspect(self.session.connection()).has_table(
            PredictiveModelRecord.__tablename__
        ):
            self._models = {}
            return self._models
        existing = {
            row.market: row
            for row in self.session.scalars(select(PredictiveModelRecord).where(
                PredictiveModelRecord.name == MODEL_NAME,
                PredictiveModelRecord.version == MODEL_VERSION,
                PredictiveModelRecord.competition_id == "global",
            )).all()
        }
        # Workers de baixa latência reutilizam o último artefato persistido.
        # O treinamento permanece no ciclo estatístico completo para não
        # bloquear a coleta frequente de odds.
        if not self.allow_training:
            self._models = {
                market: dict(row.parameters)
                for market, row in existing.items()
            }
            return self._models

        samples = self._dataset()
        # Mantém uma janela temporal ampla, porém limitada. Isso impede que o
        # primeiro treino monopolize o scheduler à medida que o histórico
        # cresce, sem misturar observações futuras ou perder o holdout.
        maximum_samples = max(
            MINIMUM_SAMPLES,
            int(os.getenv("TEMPORAL_ML_MAXIMUM_SAMPLES", str(MAXIMUM_SAMPLES))),
        )
        samples = samples[-maximum_samples:]
        # Inclui atributos e alvos: uma correção tardia de placar/estatística
        # precisa invalidar o artefato mesmo quando os IDs não mudam.
        checksum_payload = [
            (
                match_id,
                tuple(round(value, 8) for value in features),
                tuple(sorted(targets.items())),
            )
            for match_id, features, targets in samples
        ]
        checksum = sha256(repr(checksum_payload).encode()).hexdigest()
        if not self.force_retraining and existing and all(
            market in existing
            and existing[market].parameters.get("dataset_checksum") == checksum
            for market in MARKETS
        ):
            self._models = {
                market: dict(existing[market].parameters)
                for market in MARKETS
            }
            return self._models

        trained: dict[str, dict[str, object]] = {}
        for market, labels in MARKETS.items():
            parameters = self._train(samples, market, len(labels), checksum)
            trained[market] = parameters
            row = existing.get(market)
            if row is None:
                row = PredictiveModelRecord(
                    name=MODEL_NAME,
                    version=MODEL_VERSION,
                    competition_id="global",
                    market=market,
                    parameters=parameters,
                )
                self.session.add(row)
            else:
                row.parameters = parameters
        self.session.flush()
        self._models = trained
        return trained

    def _dataset(self) -> list[tuple[int, list[float], dict[str, int]]]:
        rows = self.session.execute(
            select(Match, MatchStatistics)
            .outerjoin(MatchStatistics, MatchStatistics.match_id == Match.id)
            .where(
                Match.status == "finished",
                Match.home_score.is_not(None),
                Match.away_score.is_not(None),
            )
            .order_by(Match.kickoff_at, Match.id)
        ).all()
        history: dict[int, deque[dict[str, float | datetime]]] = defaultdict(
            lambda: deque(maxlen=20)
        )
        samples: list[tuple[int, list[float], dict[str, int]]] = []
        for match, statistics in rows:
            home_history = history[match.home_team_id]
            away_history = history[match.away_team_id]
            if len(home_history) >= 5 and len(away_history) >= 5:
                features = self._feature_vector(
                    home_history, away_history, match.kickoff_at
                )
                total = int(match.home_score) + int(match.away_score)
                samples.append((
                    match.id,
                    features,
                    {
                        "match_winner": (
                            0 if match.home_score > match.away_score
                            else 1 if match.home_score == match.away_score else 2
                        ),
                        "over_2_5_goals": int(total > 2),
                        "both_teams_to_score": int(
                            match.home_score > 0 and match.away_score > 0
                        ),
                    },
                ))
            self._append_history(
                history[match.home_team_id], match, statistics, home=True
            )
            self._append_history(
                history[match.away_team_id], match, statistics, home=False
            )
        return samples

    @staticmethod
    def _append_history(history, match, statistics, *, home: bool) -> None:
        scored = float(match.home_score if home else match.away_score)
        conceded = float(match.away_score if home else match.home_score)
        prefix, opponent = ("home", "away") if home else ("away", "home")
        value = lambda name, fallback: float(
            getattr(statistics, f"{name}_{prefix}", None)
            if statistics is not None else fallback
        ) if statistics is not None and getattr(
            statistics, f"{name}_{prefix}", None
        ) is not None else float(fallback)
        opponent_value = lambda name, fallback: float(
            getattr(statistics, f"{name}_{opponent}", None)
            if statistics is not None else fallback
        ) if statistics is not None and getattr(
            statistics, f"{name}_{opponent}", None
        ) is not None else float(fallback)
        history.append({
            "at": match.kickoff_at,
            "gf": scored,
            "ga": conceded,
            "points": 3.0 if scored > conceded else 1.0 if scored == conceded else 0.0,
            "xgf": value("xg", scored),
            "xga": opponent_value("xg", conceded),
            "sot": value("shots_on_target", scored * 2.0),
            "corners": value("corners", 5.0),
            "cards": value("yellow_cards", 2.0) + value("red_cards", 0.0),
        })

    @classmethod
    def _feature_vector(cls, home, away, kickoff: datetime) -> list[float]:
        kickoff_utc = cls._naive_utc(kickoff)

        def summary(rows):
            weights = [0.90 ** index for index in range(len(rows))]
            recent = list(reversed(rows))
            total = sum(weights)
            weighted = lambda key: sum(
                float(item[key]) * weight
                for item, weight in zip(recent, weights)
            ) / total
            last_at = cls._naive_utc(recent[0]["at"])
            return {
                key: weighted(key)
                for key in ("gf", "ga", "points", "xgf", "xga", "sot", "corners", "cards")
            } | {
                "rest": min(
                    30.0,
                    max(
                        0.0,
                        (kickoff_utc - last_at).total_seconds() / 86400,
                    ),
                ),
                "sample": min(1.0, len(rows) / 20),
            }
        h, a = summary(home), summary(away)
        return [
            h["gf"] - a["ga"], a["gf"] - h["ga"],
            h["points"] - a["points"], h["xgf"] - a["xga"],
            a["xgf"] - h["xga"], h["sot"] - a["sot"],
            h["corners"] - a["corners"], h["cards"] - a["cards"],
            h["rest"] - a["rest"], h["sample"], a["sample"],
        ]

    @staticmethod
    def _naive_utc(value: datetime) -> datetime:
        """Normaliza datas do provider e do banco para a mesma linha temporal.

        O PostgreSQL pode devolver ``timestamp without time zone`` como uma
        data ingênua, enquanto a API-Football fornece ISO-8601 com offset. Os
        valores ingênuos do domínio já representam UTC; os conscientes são
        convertidos para UTC antes da remoção do ``tzinfo``.
        """
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def _features_for_match(self, match: Match) -> list[float] | None:
        kickoff = self._naive_utc(match.kickoff_at)
        histories = []
        for team_id in (match.home_team_id, match.away_team_id):
            rows = self.session.execute(
                select(Match, MatchStatistics)
                .outerjoin(MatchStatistics, MatchStatistics.match_id == Match.id)
                .where(
                    Match.status == "finished",
                    Match.kickoff_at < kickoff,
                    (
                        (Match.home_team_id == team_id)
                        | (Match.away_team_id == team_id)
                    ),
                )
                .order_by(Match.kickoff_at.desc())
                .limit(20)
            ).all()
            history = deque(maxlen=20)
            for old, statistics in reversed(rows):
                self._append_history(
                    history, old, statistics, home=old.home_team_id == team_id
                )
            histories.append(history)
        if any(len(history) < 5 for history in histories):
            return None
        return self._feature_vector(histories[0], histories[1], kickoff)

    def _train(self, samples, market, classes, checksum) -> dict[str, object]:
        size = len(samples)
        if size < MINIMUM_SAMPLES:
            return {
                "approved": False, "samples": size,
                "reason": "insufficient_temporal_samples",
                "dataset_checksum": checksum,
            }
        train_end, calibration_end = int(size * .70), int(size * .85)
        train, calibration, test = (
            samples[:train_end], samples[train_end:calibration_end],
            samples[calibration_end:],
        )
        feature_count = len(train[0][1])
        means = [mean(item[1][index] for item in train) for index in range(feature_count)]
        scales = [
            max(1e-6, (
                mean((item[1][index] - means[index]) ** 2 for item in train)
            ) ** .5)
            for index in range(feature_count)
        ]
        transform = lambda values: [
            (value - means[index]) / scales[index]
            for index, value in enumerate(values)
        ]
        weights = [[0.0] * (feature_count + 1) for _ in range(classes)]
        learning_rate, regularization = .04, .002
        for _ in range(TRAINING_EPOCHS):
            gradients = [[0.0] * (feature_count + 1) for _ in range(classes)]
            for _, raw, targets in train:
                values = [1.0, *transform(raw)]
                probabilities = self._softmax([
                    sum(weight * value for weight, value in zip(row, values))
                    for row in weights
                ])
                target = targets[market]
                for category in range(classes):
                    error = probabilities[category] - int(category == target)
                    for index, value in enumerate(values):
                        gradients[category][index] += error * value
            for category in range(classes):
                for index in range(feature_count + 1):
                    penalty = 0.0 if index == 0 else regularization * weights[category][index]
                    weights[category][index] -= learning_rate * (
                        gradients[category][index] / len(train) + penalty
                    )
        temperature = min(
            (value / 20 for value in range(10, 41)),
            key=lambda value: self._log_loss(
                calibration, market, weights, means, scales, value
            ),
        )
        test_loss = self._log_loss(test, market, weights, means, scales, temperature)
        accuracy = self._accuracy(test, market, weights, means, scales, temperature)
        baseline = self._baseline_loss(train, test, market, classes)
        baseline_probabilities = self._baseline_probabilities(train, market, classes)
        parameters = {
            "weights": weights, "means": means, "scales": scales,
            "temperature": temperature,
        }
        improvements = [
            -log(baseline_probabilities[targets[market]])
            + log(max(1e-12, self._infer(raw, parameters)[targets[market]]))
            for _, raw, targets in test
        ]
        improvement = (baseline - test_loss) / baseline if baseline else 0.0
        standard_error = pstdev(improvements) / sqrt(len(improvements)) if len(improvements) > 1 else 99.0
        ci_low = mean(improvements) - 1.96 * standard_error if improvements else -99.0
        ci_high = mean(improvements) + 1.96 * standard_error if improvements else 99.0
        minimum_improvement = float(os.getenv("TEMPORAL_ML_MIN_RELATIVE_IMPROVEMENT", "0.01"))
        approved = bool(test and improvement >= minimum_improvement and ci_low > 0)
        return {
            "approved": approved,
            "samples": size,
            "train_samples": len(train),
            "calibration_samples": len(calibration),
            "test_samples": len(test),
            "features": [
                "home_attack", "away_attack", "form_difference",
                "home_xg_edge", "away_xg_edge", "shots_on_target_edge",
                "corner_edge", "card_edge", "rest_edge",
                "home_sample_reliability", "away_sample_reliability",
            ],
            "means": means, "scales": scales, "weights": weights,
            "temperature": temperature,
            "test_log_loss": test_loss, "baseline_log_loss": baseline,
            "relative_improvement": improvement,
            "improvement_confidence_interval_95": [ci_low, ci_high],
            "minimum_relative_improvement": minimum_improvement,
            "test_accuracy": accuracy,
            "validation": "chronological_70_15_15",
            "calibration": "temperature_on_holdout",
            "dataset_checksum": checksum,
        }

    @classmethod
    def _infer(cls, raw, parameters) -> list[float]:
        means, scales = parameters["means"], parameters["scales"]
        values = [1.0, *[
            (value - means[index]) / scales[index]
            for index, value in enumerate(raw)
        ]]
        logits = [
            sum(weight * value for weight, value in zip(row, values))
            / float(parameters["temperature"])
            for row in parameters["weights"]
        ]
        return cls._softmax(logits)

    @staticmethod
    def _softmax(logits: list[float]) -> list[float]:
        maximum = max(logits)
        values = [exp(value - maximum) for value in logits]
        total = sum(values)
        return [value / total for value in values]

    @classmethod
    def _log_loss(cls, rows, market, weights, means, scales, temperature):
        if not rows:
            return 99.0
        parameters = {
            "weights": weights, "means": means, "scales": scales,
            "temperature": temperature,
        }
        return mean(
            -log(max(1e-12, cls._infer(raw, parameters)[targets[market]]))
            for _, raw, targets in rows
        )

    @classmethod
    def _accuracy(cls, rows, market, weights, means, scales, temperature):
        if not rows:
            return 0.0
        parameters = {
            "weights": weights, "means": means, "scales": scales,
            "temperature": temperature,
        }
        return mean(
            int(max(range(len(probabilities)), key=probabilities.__getitem__) == targets[market])
            for _, raw, targets in rows
            for probabilities in (cls._infer(raw, parameters),)
        )

    @staticmethod
    def _baseline_loss(train, test, market, classes):
        probabilities = TemporalMLService._baseline_probabilities(train, market, classes)
        return mean(
            -log(probabilities[targets[market]]) for _, _, targets in test
        ) if test else 99.0

    @staticmethod
    def _baseline_probabilities(train, market, classes):
        counts = [1.0] * classes
        for _, _, targets in train:
            counts[targets[market]] += 1
        total = sum(counts)
        return [count / total for count in counts]
