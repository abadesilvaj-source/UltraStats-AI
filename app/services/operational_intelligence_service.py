from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import sqrt
from hashlib import sha256
from statistics import mean
import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Audit,
    Market,
    Match,
    Odd,
    Prediction,
)
from ultrastats_ai.infrastructure.database.models import (
    ModelBacktestRecord,
    ModelValidationRecord,
    PredictiveModelRecord,
    RecommendationOpportunityRecord,
    TrainingDatasetRecord,
)


class OperationalIntelligenceService:
    """Materializa recomendações e o estado auditável do ciclo de ML."""

    model_name = "operational_poisson"
    model_version = "operational-poisson-v1"

    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self) -> dict[str, object]:
        lifecycle = self._materialize_model_lifecycle()
        recommendations = self._materialize_recommendations(
            model_approved=bool(lifecycle["model_approved"])
        )
        return {
            **lifecycle,
            "recommendations_persisted": recommendations,
        }

    def _materialize_model_lifecycle(self) -> dict[str, object]:
        model = self.session.scalar(
            select(PredictiveModelRecord).where(
                PredictiveModelRecord.name == self.model_name,
                PredictiveModelRecord.version == self.model_version,
                PredictiveModelRecord.competition_id == "global",
                PredictiveModelRecord.market == "multi_market",
            )
        )
        if model is None:
            model = PredictiveModelRecord(
                name=self.model_name,
                version=self.model_version,
                competition_id="global",
                market="multi_market",
                parameters={
                    "family": "poisson",
                    "online_team_rating_alpha": 0.18,
                    "calibration": "empirical_bayesian",
                    "validation": "walk_forward",
                    "role": "champion",
                },
            )
            self.session.add(model)
        challenger = self.session.scalar(
            select(PredictiveModelRecord).where(
                PredictiveModelRecord.name
                == "operational_calibrated_ensemble",
                PredictiveModelRecord.version == "challenger-v1",
                PredictiveModelRecord.competition_id == "global",
                PredictiveModelRecord.market == "multi_market",
            )
        )
        if challenger is None:
            self.session.add(
                PredictiveModelRecord(
                    name="operational_calibrated_ensemble",
                    version="challenger-v1",
                    competition_id="global",
                    market="multi_market",
                    parameters={
                        "family": "weighted_ensemble",
                        "members": [
                            "poisson",
                            "online_team_ratings",
                            "empirical_calibration",
                        ],
                        "weights": [0.60, 0.25, 0.15],
                        "role": "challenger",
                        "promotion_policy":
                            "lower_walk_forward_brier",
                    },
                )
            )

        audits = self.session.scalars(
            select(Audit)
            .where(
                Audit.source == "automatic_learning_pipeline",
                Audit.result_status.in_(("won", "lost")),
            )
            .order_by(Audit.audited_at)
        ).all()
        checksum = sha256(
            "|".join(
                f"{item.id}:{item.result_status}:"
                f"{item.predicted_probability}"
                for item in audits
            ).encode()
        ).hexdigest()
        dataset = self.session.scalar(
            select(TrainingDatasetRecord).where(
                TrainingDatasetRecord.checksum == checksum
            )
        )
        if dataset is None:
            dataset = TrainingDatasetRecord(
                name="automatic_post_match_audits",
                version=f"{datetime.now(timezone.utc):%Y%m%d}-{checksum[:12]}",
                cutoff_at=datetime.now(timezone.utc),
                samples=len(audits),
                feature_schema={
                    "prediction": "probability",
                    "target": "won",
                    "grouping": "model_market",
                },
                provider_coverage=self._provider_coverage(),
                checksum=checksum,
                created_at=datetime.now(timezone.utc),
            )
            self.session.add(dataset)
            self.session.flush()

            brier = self._brier(audits)
            calibration_error = self._calibration_error(audits)
            walk_forward = self._walk_forward_metrics(audits)
            per_market = self._per_market_metrics(audits)
            drift = bool(
                walk_forward["baseline_brier"] is not None
                and walk_forward["recent_brier"] is not None
                and walk_forward["recent_brier"]
                > walk_forward["baseline_brier"] + float(
                    os.getenv("MODEL_DRIFT_BRIER_DELTA", "0.08")
                )
            )
            minimum = 20
            failures = []
            if len(audits) < minimum:
                failures.append("insufficient_samples")
            if brier is not None and brier > 0.30:
                failures.append("brier_score")
            if calibration_error is not None and calibration_error > 0.20:
                failures.append("calibration_error")
            if drift:
                failures.append("model_drift")
            metrics = {
                "brier_score": brier,
                "calibration_error": calibration_error,
                "samples": len(audits),
                "walk_forward": walk_forward,
                "per_market": per_market,
                "drift_detected": drift,
                "champion": self.model_version,
                "challenger": "challenger-v1",
            }
            self.session.add(
                ModelBacktestRecord(
                    model_name=self.model_name,
                    model_version=self.model_version,
                    samples=len(audits),
                    metrics=metrics,
                    evaluated_at=datetime.now(timezone.utc),
                )
            )
            self.session.add(
                ModelValidationRecord(
                    model_name=self.model_name,
                    model_version=self.model_version,
                    dataset_id=dataset.id,
                    metrics=metrics,
                    gate_failures=failures,
                    approved=not failures,
                    evaluated_at=datetime.now(timezone.utc),
                )
            )
        else:
            validation = self.session.scalar(
                select(ModelValidationRecord).where(
                    ModelValidationRecord.dataset_id == dataset.id
                )
            )
            failures = (
                validation.gate_failures if validation else []
            )
        return {
            "training_samples": len(audits),
            "model_approved": not failures,
            "model_gate_failures": failures,
        }

    def _materialize_recommendations(
        self, *, model_approved: bool
    ) -> int:
        now = datetime.now(timezone.utc)
        matches = self.session.scalars(
            select(Match).where(
                Match.status.in_(("scheduled", "in_progress")),
                Match.kickoff_at >= now.replace(tzinfo=None)
                - timedelta(hours=2),
                Match.kickoff_at <= now.replace(tzinfo=None)
                + timedelta(days=14),
            )
        ).all()
        created = 0
        for match in matches:
            predictions = self.session.scalars(
                select(Prediction)
                .where(
                    Prediction.match_id == match.id,
                    Prediction.model_version == self.model_version,
                )
                .order_by(
                    Prediction.market_id,
                    Prediction.probability.desc(),
                )
            ).all()
            best: dict[int, Prediction] = {}
            for prediction in predictions:
                best.setdefault(prediction.market_id, prediction)
            for prediction in best.values():
                market = self.session.get(Market, prediction.market_id)
                odd = self.session.scalar(
                    select(Odd)
                    .where(
                        Odd.match_id == match.id,
                        Odd.market_id == prediction.market_id,
                        Odd.selection == prediction.selection,
                    )
                    .order_by(
                        Odd.odd_value.desc(),
                        Odd.collected_at.desc(),
                    )
                )
                reasons = []
                warnings = []
                if odd is None:
                    reasons.append("missing_odds")
                odd_age_hours = (
                    (
                        now.replace(tzinfo=None) - odd.collected_at
                    ).total_seconds() / 3600
                    if odd else None
                )
                maximum_odds_age = float(
                    os.getenv("ODDS_MAX_AGE_HOURS", "6")
                )
                if (
                    odd_age_hours is not None
                    and odd_age_hours > maximum_odds_age
                ):
                    reasons.append("stale_odds")
                sample_size = self._market_sample_size(
                    prediction.market_id
                )
                margin = 1.96 * sqrt(
                    prediction.probability
                    * (1 - prediction.probability)
                    / max(20, sample_size)
                )
                probability_low = max(
                    0.01, prediction.probability - margin
                )
                conservative_ev = (
                    probability_low * float(odd.odd_value) - 1
                    if odd else None
                )
                if prediction.expected_value is None:
                    reasons.append("missing_expected_value")
                minimum_edge = float(
                    os.getenv(
                        "RECOMMENDATION_MIN_CONSERVATIVE_EV", "0.02"
                    )
                )
                if (
                    prediction.expected_value is not None
                    and (
                    conservative_ev is None
                    or conservative_ev < minimum_edge
                    )
                ):
                    reasons.append("insufficient_conservative_edge")
                if prediction.evidence_level == "low":
                    warnings.append("low_evidence")
                if sample_size < 50:
                    warnings.append("limited_market_sample")
                if not model_approved:
                    reasons.append("model_validation_failed")
                safe = not reasons
                kelly = (
                    max(
                        0.0,
                        (
                            probability_low * float(odd.odd_value) - 1
                        )
                        / (float(odd.odd_value) - 1),
                    )
                    if odd and float(odd.odd_value) > 1 else 0.0
                )
                self.session.add(
                    RecommendationOpportunityRecord(
                        match_id=str(match.id),
                        market=market.code,
                        selection=prediction.selection,
                        bookmaker=odd.bookmaker if odd else None,
                        offered_odds=(
                            str(odd.odd_value) if odd else None
                        ),
                        metrics={
                            "probability": prediction.probability,
                            "implied_probability":
                                prediction.implied_probability,
                            "expected_value": prediction.expected_value,
                            "conservative_expected_value":
                                conservative_ev,
                            "confidence": prediction.confidence,
                            "model_version": prediction.model_version,
                            "warnings": warnings,
                            "probability_interval": {
                                "low": probability_low,
                                "high": min(
                                    0.99,
                                    prediction.probability + margin,
                                ),
                            },
                            "market_samples": sample_size,
                            "odds_age_hours": odd_age_hours,
                            "fractional_kelly": kelly * 0.25,
                        },
                        risk=prediction.risk_level,
                        score=str(
                            max(
                                0.0,
                                min(
                                    1.0,
                                    prediction.confidence
                                    + max(
                                        0.0,
                                        conservative_ev or 0.0,
                                    ),
                                ),
                            )
                        ),
                        safe=safe,
                        blocked_reasons=reasons,
                        explanation=[
                            f"Probabilidade do modelo: "
                            f"{prediction.probability:.1%}",
                            (
                                f"EV conservador: "
                                f"{conservative_ev:.3f}"
                                if conservative_ev is not None
                                else "Sem odds conciliadas"
                            ),
                            *(
                                [
                                    "Evidência ainda limitada; use uma "
                                    "exposição menor."
                                ]
                                if warnings else []
                            ),
                        ],
                        correlation_key=(
                            f"{match.competition_id}:"
                            f"{prediction.market_id}:"
                            f"{prediction.selection}"
                        ),
                        evaluated_at=now,
                    )
                )
                created += 1
        return created

    def _provider_coverage(self) -> dict[str, object]:
        return {
            "football_data_uk": "historical_ratings",
            "api_football": "results_and_statistics",
            "sportmonks": "complementary",
            "the_odds_api": "market_prices",
        }

    def _market_sample_size(self, market_id: int) -> int:
        return len(
            self.session.scalars(
                select(Audit.id)
                .join(Prediction, Prediction.id == Audit.prediction_id)
                .where(
                    Prediction.market_id == market_id,
                    Audit.result_status.in_(("won", "lost")),
                )
            ).all()
        )

    def _per_market_metrics(
        self, audits: list[Audit]
    ) -> dict[str, dict[str, float | int | None]]:
        grouped: dict[int, list[Audit]] = {}
        prediction_market = dict(
            self.session.execute(
                select(Prediction.id, Prediction.market_id).where(
                    Prediction.id.in_(
                        [
                            item.prediction_id for item in audits
                            if item.prediction_id is not None
                        ] or [-1]
                    )
                )
            ).all()
        )
        for item in audits:
            market_id = prediction_market.get(item.prediction_id)
            if market_id is not None:
                grouped.setdefault(market_id, []).append(item)
        names = {
            item.id: item.code
            for item in self.session.scalars(select(Market)).all()
        }
        return {
            names.get(market_id, str(market_id)): {
                "samples": len(items),
                "brier_score": self._brier(items),
                "calibration_error": self._calibration_error(items),
            }
            for market_id, items in grouped.items()
        }

    def _walk_forward_metrics(
        self, audits: list[Audit]
    ) -> dict[str, float | int | None]:
        if len(audits) < 10:
            return {
                "training_samples": len(audits),
                "validation_samples": 0,
                "baseline_brier": self._brier(audits),
                "recent_brier": None,
            }
        split = max(1, int(len(audits) * 0.70))
        baseline, recent = audits[:split], audits[split:]
        return {
            "training_samples": len(baseline),
            "validation_samples": len(recent),
            "baseline_brier": self._brier(baseline),
            "recent_brier": self._brier(recent),
        }

    @staticmethod
    def _brier(audits: list[Audit]) -> float | None:
        return (
            mean(
                (
                    float(item.predicted_probability or 0)
                    - (1.0 if item.result_status == "won" else 0.0)
                ) ** 2
                for item in audits
            )
            if audits else None
        )

    @staticmethod
    def _calibration_error(audits: list[Audit]) -> float | None:
        if not audits:
            return None
        predicted = mean(
            float(item.predicted_probability or 0)
            for item in audits
        )
        observed = mean(
            1.0 if item.result_status == "won" else 0.0
            for item in audits
        )
        return abs(predicted - observed)
