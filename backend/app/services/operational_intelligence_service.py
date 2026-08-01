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
    Bet,
    Competition,
    Market,
    Match,
    Odd,
    Prediction,
)
from app.core.competition_catalog import competition_policy
from app.utils.odds_matching import best_matching_odd, canonical_selection
from app.services.intelligence_platform_service import (
    IntelligencePlatformService,
    market_family,
)
from ultrastats_ai.infrastructure.database.models import (
    DecisionPolicyRecord,
    ModelBacktestRecord,
    ModelValidationRecord,
    PredictiveModelRecord,
    RecommendationOpportunityRecord,
    TrainingDatasetRecord,
    RawProviderPayloadRecord,
)


class OperationalIntelligenceService:
    """Materializa recomendações e o estado auditável do ciclo de ML."""

    model_name = "operational_poisson"
    model_version = "operational-poisson-v1"

    def __init__(self, session: Session) -> None:
        self.session = session
        self._market_samples_cache: dict[int, int] | None = None

    def run(self) -> dict[str, object]:
        lifecycle = self._materialize_model_lifecycle()
        platform = IntelligencePlatformService(self.session).run()
        self.session.flush()
        recommendations = self._materialize_recommendations(
            model_approved=bool(lifecycle["model_approved"])
        )
        return {
            **lifecycle,
            "recommendations_persisted": recommendations,
            "platform": platform,
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

        audit_rows = self.session.execute(
            select(Audit, Competition)
            .join(Prediction, Prediction.id == Audit.prediction_id)
            .join(Match, Match.id == Prediction.match_id)
            .join(Competition, Competition.id == Match.competition_id)
            .where(
                Audit.source == "automatic_learning_pipeline",
                Audit.result_status.in_(("won", "lost")),
            )
            .order_by(Audit.audited_at)
        ).all()
        audits = [
            audit for audit, competition in audit_rows
            if competition_policy(
                competition.name, competition.country
            ) is not None
        ]
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
        segment_metrics: dict[str, dict[str, object]] = {}
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
            per_competition_market = (
                self._per_competition_market_metrics(audits)
            )
            segment_metrics = per_competition_market
            drift = bool(
                walk_forward["baseline_brier"] is not None
                and walk_forward["recent_brier"] is not None
                and walk_forward["recent_brier"]
                > walk_forward["baseline_brier"] + float(
                    os.getenv("MODEL_DRIFT_BRIER_DELTA", "0.08")
                )
            )
            minimum = int(os.getenv("MODEL_MIN_GLOBAL_SAMPLES", "100"))
            failures = []
            if len(audits) < minimum:
                failures.append("insufficient_samples")
            if brier is not None and brier > 0.30:
                failures.append("brier_score")
            if calibration_error is not None and calibration_error > 0.20:
                failures.append("calibration_error")
            if (
                walk_forward["recent_brier"] is not None
                and walk_forward["recent_brier"] > float(
                    os.getenv("MODEL_MAX_RECENT_BRIER", "0.26")
                )
            ):
                failures.append("recent_brier_score")
            if drift:
                failures.append("model_drift")
            metrics = {
                "brier_score": brier,
                "calibration_error": calibration_error,
                "samples": len(audits),
                "walk_forward": walk_forward,
                "per_market": per_market,
                "per_competition_market": per_competition_market,
                "drift_detected": drift,
                "champion": self.model_version,
                "challenger": "challenger-v1",
                "financial": self._financial_metrics(),
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
            segment_metrics = (
                validation.metrics.get(
                    "per_competition_market", {}
                )
                if validation else {}
            )
        self._materialize_segment_models(segment_metrics)
        return {
            "training_samples": len(audits),
            "model_approved": not failures,
            "model_gate_failures": failures,
        }

    def _materialize_segment_models(
        self, metrics: dict[str, dict[str, object]]
    ) -> None:
        """Registra segmentos confiáveis sem substituir o campeão global."""
        minimum = int(os.getenv(
            "MODEL_MIN_COMPETITION_MARKET_SAMPLES", "20"
        ))
        for key, values in metrics.items():
            if int(values.get("samples") or 0) < minimum or ":" not in key:
                continue
            competition, market = key.split(":", 1)
            record = self.session.scalar(
                select(PredictiveModelRecord).where(
                    PredictiveModelRecord.name
                    == "competition_market_calibrator",
                    PredictiveModelRecord.version == "segment-v1",
                    PredictiveModelRecord.competition_id == competition,
                    PredictiveModelRecord.market == market,
                )
            )
            parameters = {
                "family": "empirical_bayesian_calibrator",
                "parent": self.model_version,
                "minimum_samples": minimum,
                "metrics": values,
                "role": "segment",
            }
            if record is None:
                self.session.add(PredictiveModelRecord(
                    name="competition_market_calibrator",
                    version="segment-v1",
                    competition_id=competition,
                    market=market,
                    parameters=parameters,
                ))
            else:
                record.parameters = parameters

    def _materialize_recommendations(
        self, *, model_approved: bool
    ) -> int:
        now = datetime.now(timezone.utc)
        validation = self.session.scalar(
            select(ModelValidationRecord)
            .where(
                ModelValidationRecord.model_name == self.model_name,
                ModelValidationRecord.model_version == self.model_version,
            )
            .order_by(ModelValidationRecord.evaluated_at.desc())
        )
        per_market = (
            validation.metrics.get("per_market", {})
            if validation else {}
        )
        per_competition_market = (
            validation.metrics.get("per_competition_market", {})
            if validation else {}
        )
        decision_policies = self.session.scalars(
            select(DecisionPolicyRecord).where(
                DecisionPolicyRecord.active.is_(True)
            )
        ).all()
        matches = self.session.scalars(
            select(Match).where(
                Match.status.in_(("scheduled", "in_progress")),
                Match.kickoff_at >= now.replace(tzinfo=None)
                - timedelta(hours=2),
                Match.kickoff_at <= now.replace(tzinfo=None)
                + timedelta(days=14),
            )
        ).all()
        match_ids = [match.id for match in matches]
        odds_by_market: dict[tuple[int, int], list[Odd]] = {}
        for current_odd in self.session.scalars(
            select(Odd).where(Odd.match_id.in_(match_ids or [-1]))
        ).all():
            odds_by_market.setdefault(
                (current_odd.match_id, current_odd.market_id), []
            ).append(current_odd)
        markets_by_id = {
            market.id: market
            for market in self.session.scalars(select(Market)).all()
        }
        created = 0
        for match in matches:
            competition = self.session.get(
                Competition, match.competition_id
            )
            policy = (
                competition_policy(
                    competition.name, competition.country
                )
                if competition else None
            )
            if policy is None:
                continue
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
                market = markets_by_id[prediction.market_id]
                market_odds = odds_by_market.get(
                    (match.id, prediction.market_id), []
                )
                reasons = []
                warnings = []
                maximum_odds_age = float(
                    os.getenv("ODDS_MAX_AGE_HOURS", "6")
                )
                odd = best_matching_odd(
                    market_odds,
                    prediction.selection,
                    now=now.replace(tzinfo=None),
                    maximum_age_hours=maximum_odds_age,
                )
                if odd is None:
                    reasons.append("missing_odds")
                odd_age_hours = (
                    (
                        now.replace(tzinfo=None) - odd.collected_at
                    ).total_seconds() / 3600
                    if odd else None
                )
                sample_size = self._market_sample_size(
                    prediction.market_id
                )
                market_metrics = per_market.get(market.code, {})
                market_approved = self._market_is_approved(
                    market_metrics
                )
                competition_market_key = (
                    f"{policy.code}:{market.code}"
                )
                competition_market_metrics = (
                    per_competition_market.get(
                        competition_market_key, {}
                    )
                )
                competition_market_approved = (
                    self._competition_market_is_approved(
                        competition_market_metrics
                    )
                )
                competition_market_sample_ready = (
                    self._competition_market_has_enough_samples(
                        competition_market_metrics
                    )
                )
                offered_odds = float(odd.odd_value) if odd else None
                horizon_hours = max(
                    0.0,
                    IntelligencePlatformService._hours_until(match.kickoff_at, now),
                )
                decision_policy = self._select_decision_policy(
                    decision_policies,
                    competition,
                    market_family(market.code),
                    offered_odds,
                    horizon_hours,
                )
                calibrated_probability = self._calibrate_probability(
                    prediction.probability, decision_policy
                )
                selected_model = (
                    f"{market_family(market.code)}-competition-segment-v2"
                    if competition_market_approved
                    else (
                        f"{market_family(market.code)}-ensemble-v2"
                        if market_approved
                        else self.model_version
                    )
                )
                prediction_regime = IntelligencePlatformService._horizon(
                    horizon_hours
                )
                selected_model = f"{selected_model}:{prediction_regime}"
                margin = 1.96 * sqrt(
                    calibrated_probability
                    * (1 - calibrated_probability)
                    / max(20, sample_size)
                )
                probability_low = max(
                    0.01, calibrated_probability - margin
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
                if not market_approved:
                    reasons.append("market_validation_failed")
                if (
                    competition_market_sample_ready
                    and not competition_market_approved
                ):
                    reasons.append(
                        "competition_market_validation_failed"
                    )
                elif not competition_market_sample_ready:
                    warnings.append(
                        "competition_market_limited_sample"
                    )
                safe = not reasons
                selection_threshold = float(
                    (decision_policy.selection_policy if decision_policy else {})
                    .get("probability_threshold", .80)
                )
                policy_drift = bool(
                    decision_policy and decision_policy.drift.get("detected")
                )
                if policy_drift:
                    warnings.append("segment_drift_detected")
                if safe and probability_low >= selection_threshold and not policy_drift:
                    recommendation_tier = "high_confidence"
                elif conservative_ev is not None and conservative_ev > 0 and not policy_drift:
                    recommendation_tier = "statistical_value"
                else:
                    recommendation_tier = "experimental"
                odds_signal = self._odds_movement(market_odds, prediction.selection)
                ensemble_weights = self._dynamic_ensemble_weights(
                    market_family(market.code), decision_policy, odds_signal
                )
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
                kelly_multiplier = {
                    "high_confidence": .25,
                    "statistical_value": .15,
                    "experimental": .05,
                }[recommendation_tier]
                fractional_kelly = min(
                    kelly * kelly_multiplier,
                    {"high_confidence": .01, "statistical_value": .005, "experimental": .0025}[
                        recommendation_tier
                    ],
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
                            "calibrated_probability": calibrated_probability,
                            "implied_probability":
                                prediction.implied_probability,
                            "expected_value": prediction.expected_value,
                            "conservative_expected_value":
                                conservative_ev,
                            "confidence": prediction.confidence,
                            "model_version": prediction.model_version,
                            "selected_model": selected_model,
                            "prediction_regime": prediction_regime,
                            "recommendation_tier": recommendation_tier,
                            "selection_threshold": selection_threshold,
                            "selective_coverage": (
                                decision_policy.selection_policy.get("coverage")
                                if decision_policy else None
                            ),
                            "calibration_segment": (
                                {
                                    "competition": decision_policy.competition,
                                    "market_family": decision_policy.market_family,
                                    "odds_band": decision_policy.odds_band,
                                    "horizon": decision_policy.horizon,
                                    "samples": decision_policy.samples,
                                } if decision_policy else None
                            ),
                            "conformal_method": "segment_conditioned_wilson_95",
                            "ensemble_weights": ensemble_weights,
                            "odds_movement": odds_signal,
                            "warnings": warnings,
                            "probability_interval": {
                                "low": probability_low,
                                "high": min(
                                    0.99,
                                    prediction.probability + margin,
                                ),
                            },
                            "market_samples": sample_size,
                            "market_validation": {
                                **market_metrics,
                                "approved": market_approved,
                            },
                            "competition": {
                                "code": policy.code,
                                "group": policy.group,
                            },
                            "competition_market_validation": {
                                **competition_market_metrics,
                                "approved":
                                    competition_market_approved,
                            },
                            "odds_age_hours": odd_age_hours,
                            "fractional_kelly": fractional_kelly,
                            "maximum_bankroll_fraction": {
                                "high_confidence": .01,
                                "statistical_value": .005,
                                "experimental": .0025,
                            }[recommendation_tier],
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
                            f"{calibrated_probability:.1%} calibrada "
                            f"({prediction.probability:.1%} bruta)",
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

    @staticmethod
    def _select_decision_policy(
        policies: list[DecisionPolicyRecord],
        competition: Competition,
        family: str,
        odds: float | None,
        horizon_hours: float,
    ) -> DecisionPolicyRecord | None:
        competition_key = f"{competition.country or 'global'}:{competition.name}"[:128]
        odds_band = IntelligencePlatformService._odds_band(odds)
        horizon = IntelligencePlatformService._horizon(horizon_hours)
        candidates = [
            item for item in policies
            if item.competition == competition_key
            and item.market_family == family
        ]
        exact = [
            item for item in candidates
            if item.odds_band == odds_band and item.horizon == horizon
        ]
        ranked = exact or candidates
        return max(ranked, key=lambda item: item.samples, default=None)

    @staticmethod
    def _calibrate_probability(
        probability: float,
        policy: DecisionPolicyRecord | None,
    ) -> float:
        if policy is None:
            return probability
        bins = policy.calibration.get("bins") or []
        selected = next(
            (
                item for item in bins
                if float(item["lower"]) <= probability < float(item["upper"])
                or (probability == 1 and float(item["upper"]) == 1)
            ),
            None,
        )
        calibrated = float(selected["calibrated"]) if selected else probability
        # Encolhimento impede que segmentos pequenos produzam 0%/100% artificiais.
        reliability = min(1.0, policy.samples / 200)
        return min(.99, max(.01, probability * (1 - reliability) + calibrated * reliability))

    @staticmethod
    def _odds_movement(
        odds: list[Odd], selection: str,
    ) -> dict[str, object]:
        matching = sorted(
            (
                item for item in odds
                if canonical_selection(item.selection) == canonical_selection(selection)
            ),
            key=lambda item: item.collected_at,
        )
        if not matching:
            return {"available": False, "samples": 0, "bookmakers": 0}
        opening = float(matching[0].odd_value)
        current = float(matching[-1].odd_value)
        hours = max(
            1 / 60,
            (matching[-1].collected_at - matching[0].collected_at).total_seconds() / 3600,
        )
        return {
            "available": True,
            "samples": len(matching),
            "bookmakers": len({item.bookmaker for item in matching}),
            "opening": opening,
            "current": current,
            "relative_change": current / opening - 1 if opening else 0,
            "velocity_per_hour": (current - opening) / hours,
            "closing_available": any(item.is_closing for item in matching),
        }

    def _dynamic_ensemble_weights(
        self,
        family: str,
        policy: DecisionPolicyRecord | None,
        odds_signal: dict[str, object],
    ) -> dict[str, float]:
        weights = dict(IntelligencePlatformService.ensemble_members.get(
            family, IntelligencePlatformService.ensemble_members["other"]
        ))
        if odds_signal.get("bookmakers", 0) >= 3 and "market" in weights:
            weights["market"] += .10
        if policy and policy.drift.get("detected"):
            for key in weights:
                weights[key] *= .85
            if "market" in weights:
                weights["market"] += .15
        total = sum(weights.values()) or 1
        return {key: round(value / total, 4) for key, value in weights.items()}

    @staticmethod
    def _market_is_approved(
        metrics: dict[str, object],
    ) -> bool:
        samples = int(metrics.get("samples") or 0)
        brier = metrics.get("brier_score")
        calibration = metrics.get("calibration_error")
        return (
            samples >= int(
                os.getenv("MODEL_MIN_MARKET_SAMPLES", "20")
            )
            and brier is not None
            and float(brier) <= float(
                os.getenv("MODEL_MAX_MARKET_BRIER", "0.30")
            )
            and calibration is not None
            and float(calibration) <= float(
                os.getenv("MODEL_MAX_MARKET_CALIBRATION_ERROR", "0.25")
            )
        )

    @staticmethod
    def _competition_market_is_approved(
        metrics: dict[str, object],
    ) -> bool:
        samples = int(metrics.get("samples") or 0)
        brier = metrics.get("brier_score")
        calibration = metrics.get("calibration_error")
        return (
            OperationalIntelligenceService
            ._competition_market_has_enough_samples(metrics)
            and brier is not None
            and float(brier) <= float(os.getenv(
                "MODEL_MAX_COMPETITION_MARKET_BRIER", "0.32"
            ))
            and calibration is not None
            and float(calibration) <= float(os.getenv(
                "MODEL_MAX_COMPETITION_MARKET_CALIBRATION_ERROR",
                "0.30",
            ))
        )

    @staticmethod
    def _competition_market_has_enough_samples(
        metrics: dict[str, object],
    ) -> bool:
        return int(metrics.get("samples") or 0) >= int(os.getenv(
            "MODEL_MIN_COMPETITION_MARKET_SAMPLES", "20"
        ))

    def _provider_coverage(self) -> dict[str, object]:
        rows = self.session.execute(
            select(
                RawProviderPayloadRecord.provider,
                RawProviderPayloadRecord.resource,
            ).distinct()
        ).all()
        coverage: dict[str, set[str]] = {}
        for provider, resource in rows:
            coverage.setdefault(provider, set()).add(resource)
        return {
            provider: {
                "role": "equal_contributor",
                "resources": sorted(resources),
            }
            for provider, resources in sorted(coverage.items())
        }

    def _market_sample_size(self, market_id: int) -> int:
        if self._market_samples_cache is None:
            from sqlalchemy import func
            self._market_samples_cache = dict(self.session.execute(
                select(Prediction.market_id, func.count(Audit.id))
                .join(Audit, Audit.prediction_id == Prediction.id)
                .where(Audit.result_status.in_(("won", "lost")))
                .group_by(Prediction.market_id)
            ).all())
        return int(self._market_samples_cache.get(market_id, 0))

    def _financial_metrics(self) -> dict[str, object]:
        bets = self.session.scalars(
            select(Bet).where(
                Bet.is_official.is_(True),
                Bet.status == "settled",
            ).order_by(Bet.settled_at, Bet.id)
        ).all()
        total_stake = sum(float(item.stake_amount or 0) for item in bets)
        total_profit = sum(
            float(item.payout_amount or 0) - float(item.stake_amount or 0)
            if item.payout_amount is not None
            and item.stake_amount is not None
            else float(item.profit_units or 0)
            for item in bets
        )
        won = sum(item.result == "won" for item in bets)
        lost = sum(item.result == "lost" for item in bets)
        equity = peak = max_drawdown = 0.0
        clv_values: list[float] = []
        for bet in bets:
            profit = (
                float(bet.payout_amount or 0) - float(bet.stake_amount or 0)
                if bet.payout_amount is not None
                and bet.stake_amount is not None
                else float(bet.profit_units or 0)
            )
            equity += profit
            peak = max(peak, equity)
            max_drawdown = max(max_drawdown, peak - equity)
            closing_rows = self.session.scalars(
                select(Odd).where(
                    Odd.match_id == bet.match_id,
                    Odd.market_id == bet.market_id,
                    Odd.is_closing.is_(True),
                ).order_by(
                    Odd.collected_at.desc(),
                    Odd.odd_value.desc(),
                )
            ).all()
            closing = next(
                (
                    odd for odd in closing_rows
                    if canonical_selection(odd.selection)
                    == canonical_selection(bet.selection)
                ),
                None,
            )
            if closing is not None and float(closing.odd_value) > 1:
                clv_values.append(
                    float(bet.odd_value) / float(closing.odd_value) - 1
                )
        decisions = won + lost
        return {
            "settled_bets": len(bets),
            "roi": total_profit / total_stake if total_stake else None,
            "yield": total_profit / total_stake if total_stake else None,
            "win_rate": won / decisions if decisions else None,
            "max_drawdown": max_drawdown,
            "average_clv": mean(clv_values) if clv_values else None,
            "clv_samples": len(clv_values),
        }

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

    def _per_competition_market_metrics(
        self, audits: list[Audit]
    ) -> dict[str, dict[str, float | int | None]]:
        prediction_ids = [
            item.prediction_id for item in audits
            if item.prediction_id is not None
        ]
        rows = self.session.execute(
            select(
                Prediction.id,
                Prediction.market_id,
                Competition.name,
                Competition.country,
            )
            .join(Match, Match.id == Prediction.match_id)
            .join(Competition, Competition.id == Match.competition_id)
            .where(Prediction.id.in_(prediction_ids or [-1]))
        ).all()
        lookup = {
            prediction_id: (market_id, name, country)
            for prediction_id, market_id, name, country in rows
        }
        market_names = {
            item.id: item.code
            for item in self.session.scalars(select(Market)).all()
        }
        grouped: dict[str, list[Audit]] = {}
        for audit in audits:
            item = lookup.get(audit.prediction_id)
            if item is None:
                continue
            market_id, name, country = item
            policy = competition_policy(name, country)
            if policy is None:
                continue
            key = f"{policy.code}:{market_names.get(market_id, market_id)}"
            grouped.setdefault(key, []).append(audit)
        return {
            key: {
                "samples": len(items),
                "brier_score": self._brier(items),
                "calibration_error": self._calibration_error(items),
                "recent_brier_score": self._brier(items[-100:]),
            }
            for key, items in grouped.items()
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
        # Expected Calibration Error por faixas evita que erros opostos se
        # anulem, como ocorria com a média global anterior.
        total = len(audits)
        error = 0.0
        for index in range(10):
            lower, upper = index / 10, (index + 1) / 10
            bucket = [
                item for item in audits
                if lower <= float(item.predicted_probability or 0)
                < upper
                or (
                    index == 9
                    and float(item.predicted_probability or 0) == 1
                )
            ]
            if not bucket:
                continue
            predicted = mean(
                float(item.predicted_probability or 0)
                for item in bucket
            )
            observed = mean(
                1.0 if item.result_status == "won" else 0.0
                for item in bucket
            )
            error += len(bucket) / total * abs(predicted - observed)
        return error
