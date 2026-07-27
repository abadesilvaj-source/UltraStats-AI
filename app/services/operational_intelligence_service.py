from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from statistics import mean

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
        recommendations = self._materialize_recommendations()
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
                },
            )
            self.session.add(model)

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

            brier = (
                mean(
                    (
                        float(item.predicted_probability or 0)
                        - (1.0 if item.result_status == "won" else 0.0)
                    ) ** 2
                    for item in audits
                )
                if audits else None
            )
            calibration_error = self._calibration_error(audits)
            minimum = 20
            failures = []
            if len(audits) < minimum:
                failures.append("insufficient_samples")
            if brier is not None and brier > 0.30:
                failures.append("brier_score")
            if calibration_error is not None and calibration_error > 0.20:
                failures.append("calibration_error")
            metrics = {
                "brier_score": brier,
                "calibration_error": calibration_error,
                "samples": len(audits),
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

    def _materialize_recommendations(self) -> int:
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
                if prediction.expected_value is None:
                    reasons.append("missing_expected_value")
                elif prediction.expected_value <= 0:
                    reasons.append("non_positive_expected_value")
                if prediction.evidence_level == "low":
                    warnings.append("low_evidence")
                safe = not reasons
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
                            "confidence": prediction.confidence,
                            "model_version": prediction.model_version,
                            "warnings": warnings,
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
                                        prediction.expected_value or 0.0,
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
                                f"Valor esperado: "
                                f"{prediction.expected_value:.3f}"
                                if prediction.expected_value is not None
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
