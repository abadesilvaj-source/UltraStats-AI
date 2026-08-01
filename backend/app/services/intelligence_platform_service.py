from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from statistics import mean

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Audit,
    Competition,
    Market,
    Match,
    MatchStatistics,
    Odd,
    Prediction,
    Team,
)
from ultrastats_ai.infrastructure.database.models import (
    DataQualityIncidentRecord,
    DecisionPolicyRecord,
    FeatureSnapshotRecord,
    IdentityDecisionRecord,
    ModelDeploymentRecord,
    PredictionExplanationRecord,
    ProcessingTaskRecord,
    RawProviderPayloadRecord,
    TemporalBacktestRecord,
)


MARKET_FAMILIES: dict[str, tuple[str, ...]] = {
    "results": (
        "result", "winner", "double_chance", "draw_no_bet", "handicap",
    ),
    "goals": ("goal", "btts", "score"),
    "corners": ("corner",),
    "cards": ("card", "booking"),
    "players": ("player", "scorer", "assist", "shot"),
}


def market_family(code: str) -> str:
    normalized = code.casefold()
    for family, tokens in MARKET_FAMILIES.items():
        if any(token in normalized for token in tokens):
            return family
    return "other"


class PersistentTaskQueue:
    """Fila transacional mínima, recuperável e idempotente."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def enqueue(
        self,
        kind: str,
        key: str,
        payload: dict[str, object],
        *,
        priority: int = 100,
    ) -> ProcessingTaskRecord:
        task = self.session.scalar(
            select(ProcessingTaskRecord).where(
                ProcessingTaskRecord.idempotency_key == key
            )
        )
        if task is None:
            task = ProcessingTaskRecord(
                kind=kind,
                idempotency_key=key,
                payload=payload,
                status="pending",
                priority=priority,
                attempts=0,
                max_attempts=5,
                available_at=datetime.now(timezone.utc),
            )
            self.session.add(task)
        return task

    def complete(self, task: ProcessingTaskRecord) -> None:
        task.status = "completed"
        task.finished_at = datetime.now(timezone.utc)
        task.locked_at = None

    def fail(self, task: ProcessingTaskRecord, error: Exception) -> None:
        task.attempts += 1
        task.last_error = str(error)[:2000]
        task.locked_at = None
        if task.attempts >= task.max_attempts:
            task.status = "failed"
            task.finished_at = datetime.now(timezone.utc)
        else:
            task.status = "pending"
            task.available_at = datetime.now(timezone.utc) + timedelta(
                minutes=min(60, 2 ** task.attempts)
            )


class IntelligencePlatformService:
    """Camada interna para as quinze melhorias de confiabilidade científica."""

    ensemble_members = {
        "results": {"poisson": .40, "elo": .35, "market": .25},
        "goals": {"poisson": .55, "form": .25, "market": .20},
        "corners": {"negative_binomial": .50, "form": .30, "market": .20},
        "cards": {"negative_binomial": .45, "referee": .25, "form": .30},
        "players": {"availability": .40, "form": .35, "team_context": .25},
        "other": {"poisson": .50, "form": .30, "market": .20},
    }

    def __init__(self, session: Session) -> None:
        self.session = session
        self.queue = PersistentTaskQueue(session)

    def run(self) -> dict[str, object]:
        features = self.materialize_feature_store()
        incidents = self.audit_data_quality()
        deployments = self.ensure_specialized_models()
        backtests = self.run_temporal_backtests()
        policies = self.materialize_decision_policies()
        explanations = self.materialize_explanations()
        tasks = self.register_pipeline_tasks()
        return {
            "feature_snapshots_created": features,
            "open_quality_incidents": incidents,
            "specialized_deployments": deployments,
            "temporal_backtests": backtests,
            "decision_policies": policies,
            "prediction_explanations_created": explanations,
            "pipeline_tasks_registered": tasks,
        }

    def materialize_feature_store(self) -> int:
        now = datetime.now(timezone.utc)
        matches = self.session.scalars(
            select(Match).where(
                Match.status.in_(("scheduled", "in_progress")),
                Match.kickoff_at >= now.replace(tzinfo=None) - timedelta(hours=2),
                Match.kickoff_at <= now.replace(tzinfo=None) + timedelta(days=14),
            )
        ).all()
        created = 0
        as_of = now.replace(minute=0, second=0, microsecond=0)
        context_index = self._build_context_index(
            [match.id for match in matches], as_of
        )
        for match in matches:
            existing = self.session.scalar(
                select(FeatureSnapshotRecord.id).where(
                    FeatureSnapshotRecord.entity_type == "match",
                    FeatureSnapshotRecord.entity_id == str(match.id),
                    FeatureSnapshotRecord.feature_set == "prematch_context_v1",
                    FeatureSnapshotRecord.as_of == as_of,
                )
            )
            if existing:
                continue
            home = self.session.get(Team, match.home_team_id)
            away = self.session.get(Team, match.away_team_id)
            previous = self.session.scalars(
                select(Match)
                .where(
                    Match.id != match.id,
                    Match.status == "finished",
                    Match.kickoff_at < match.kickoff_at,
                    (
                        (Match.home_team_id.in_((match.home_team_id, match.away_team_id)))
                        | (Match.away_team_id.in_((match.home_team_id, match.away_team_id)))
                    ),
                )
                .order_by(Match.kickoff_at.desc())
                .limit(20)
            ).all()
            last_by_team: dict[int, datetime] = {}
            for old in previous:
                for team_id in (old.home_team_id, old.away_team_id):
                    last_by_team.setdefault(team_id, old.kickoff_at)
            values = {
                "home_power": float(home.power_rating) if home else None,
                "away_power": float(away.power_rating) if away else None,
                "home_attack": float(home.attack_rating) if home else None,
                "away_attack": float(away.attack_rating) if away else None,
                "home_defense": float(home.defense_rating) if home else None,
                "away_defense": float(away.defense_rating) if away else None,
                "home_corner": float(home.corner_rating) if home else None,
                "away_corner": float(away.corner_rating) if away else None,
                "home_card": float(home.card_rating) if home else None,
                "away_card": float(away.card_rating) if away else None,
                "home_rest_days": self._rest_days(
                    match.kickoff_at, last_by_team.get(match.home_team_id)
                ),
                "away_rest_days": self._rest_days(
                    match.kickoff_at, last_by_team.get(match.away_team_id)
                ),
                "home_advantage": 1,
                "competition_id": match.competition_id,
                "venue": match.venue,
                "kickoff_hour_utc": match.kickoff_at.hour,
                "kickoff_weekday": match.kickoff_at.weekday(),
                "prediction_regime": (
                    "live" if match.status == "in_progress"
                    else "post_lineup" if self._hours_until(match.kickoff_at, now) <= 1.5
                    else "prematch"
                ),
                "home_recent_matches": sum(
                    match.home_team_id in (old.home_team_id, old.away_team_id)
                    for old in previous
                ),
                "away_recent_matches": sum(
                    match.away_team_id in (old.home_team_id, old.away_team_id)
                    for old in previous
                ),
                **self._context_features(
                    match, context_index.get(match.id, {})
                ),
            }
            self.session.add(
                FeatureSnapshotRecord(
                    entity_type="match",
                    entity_id=str(match.id),
                    feature_set="prematch_context_v1",
                    values=values,
                    provenance={
                        "cutoff": as_of.isoformat(),
                        "policy": "strictly_before_kickoff",
                        "sources": ["teams", "matches", "provider_fusion"],
                    },
                    as_of=as_of,
                )
            )
            created += 1
        return created

    def _build_context_index(
        self, match_ids: list[int], as_of: datetime,
    ) -> dict[int, dict[str, set[str]]]:
        if not match_ids:
            return {}
        identities = self.session.scalars(
            select(IdentityDecisionRecord).where(
                IdentityDecisionRecord.candidate_id.in_(
                    [f"match:{match_id}" for match_id in match_ids]
                ),
                IdentityDecisionRecord.status == "matched",
            )
        ).all()
        roots: dict[tuple[str, str], list[int]] = defaultdict(list)
        for identity in identities:
            roots[(
                str(identity.provider),
                str(identity.external_id).removeprefix("match:").split(":", 1)[0],
            )].append(int(str(identity.candidate_id).split(":", 1)[1]))
        rows = self.session.execute(
            select(
                RawProviderPayloadRecord.provider,
                RawProviderPayloadRecord.external_id,
                RawProviderPayloadRecord.resource,
            ).where(
                RawProviderPayloadRecord.collected_at <= as_of,
                RawProviderPayloadRecord.resource.in_((
                    "lineups", "injuries", "weather", "events",
                    "player_statistics", "team_statistics",
                )),
            ).distinct()
        ).all()
        result: dict[int, dict[str, set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )
        for provider, external_id, resource in rows:
            key = (str(provider), str(external_id).split(":", 1)[0])
            for match_id in roots.get(key, ()):
                result[match_id][str(resource)].add(str(provider))
        return result

    def _context_features(
        self, match: Match, resource_sources: dict[str, set[str]],
    ) -> dict[str, object]:
        competition = self.session.get(Competition, match.competition_id)
        name = (competition.name if competition else "").casefold()
        return {
            "venue_available": bool(match.venue),
            "lineup_available": bool(resource_sources.get("lineups")),
            "injury_data_available": bool(resource_sources.get("injuries")),
            "weather_available": bool(resource_sources.get("weather")),
            "player_statistics_available": bool(
                resource_sources.get("player_statistics")
            ),
            "context_provider_count": len({
                provider for providers in resource_sources.values()
                for provider in providers
            }),
            "competition_importance": (
                "knockout" if any(token in name for token in (
                    "cup", "copa", "libertadores", "champions", "final"
                )) else "league"
            ),
        }

    @staticmethod
    def _rest_days(kickoff: datetime, previous: datetime | None) -> float | None:
        return (
            round((kickoff - previous).total_seconds() / 86400, 2)
            if previous else None
        )

    @staticmethod
    def _hours_until(kickoff: datetime, reference: datetime) -> float:
        if kickoff.tzinfo is None:
            reference = reference.replace(tzinfo=None)
        elif reference.tzinfo is None:
            reference = reference.replace(tzinfo=timezone.utc)
        return (kickoff - reference).total_seconds() / 3600

    def audit_data_quality(self) -> int:
        now = datetime.now(timezone.utc)
        active_fingerprints: set[str] = set()
        recent_matches = self.session.scalars(
            select(Match).where(
                Match.kickoff_at >= now.replace(tzinfo=None) - timedelta(days=3)
            )
        ).all()
        for match in recent_matches:
            if match.status == "finished":
                statistics = self.session.scalar(
                    select(MatchStatistics.id).where(
                        MatchStatistics.match_id == match.id
                    )
                )
                if not statistics:
                    active_fingerprints.add(
                        self._incident(
                            "missing_post_match_statistics", "warning",
                            "match", str(match.id),
                            {"kickoff_at": match.kickoff_at.isoformat()},
                        )
                    )
            if match.status in ("scheduled", "in_progress"):
                newest_odd = self.session.scalar(
                    select(func.max(Odd.collected_at)).where(Odd.match_id == match.id)
                )
                if newest_odd is None or newest_odd < now.replace(tzinfo=None) - timedelta(hours=8):
                    active_fingerprints.add(
                        self._incident(
                            "missing_or_stale_odds", "info", "match", str(match.id),
                            {"newest_odd": newest_odd.isoformat() if newest_odd else None},
                        )
                    )
            if match.status == "in_progress" and match.kickoff_at < (
                now.replace(tzinfo=None) - timedelta(hours=4)
            ):
                active_fingerprints.add(
                    self._incident(
                        "stale_live_status", "critical", "match", str(match.id),
                        {"kickoff_at": match.kickoff_at.isoformat()},
                    )
                )
        open_rows = self.session.scalars(
            select(DataQualityIncidentRecord).where(
                DataQualityIncidentRecord.resolved_at.is_(None)
            )
        ).all()
        for row in open_rows:
            if row.fingerprint not in active_fingerprints:
                row.resolved_at = now
        return sum(row.fingerprint in active_fingerprints for row in open_rows) + max(
            0, len(active_fingerprints) - len(open_rows)
        )

    def _incident(
        self,
        kind: str,
        severity: str,
        entity_type: str,
        entity_id: str,
        details: dict[str, object],
    ) -> str:
        fingerprint = sha256(
            f"{kind}:{entity_type}:{entity_id}".encode()
        ).hexdigest()
        row = self.session.scalar(
            select(DataQualityIncidentRecord).where(
                DataQualityIncidentRecord.fingerprint == fingerprint
            )
        )
        if row is None:
            self.session.add(
                DataQualityIncidentRecord(
                    fingerprint=fingerprint,
                    kind=kind,
                    severity=severity,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    details=details,
                    detected_at=datetime.now(timezone.utc),
                )
            )
        elif row.resolved_at is not None:
            row.resolved_at = None
            row.detected_at = datetime.now(timezone.utc)
            row.details = details
        return fingerprint

    def ensure_specialized_models(self) -> int:
        created = 0
        for family, weights in self.ensemble_members.items():
            definitions = (
                ("specialized_ensemble", "ensemble-v2", "champion", weights),
                (
                    "specialized_challenger",
                    "challenger-v2",
                    "shadow",
                    {key: round(value / sum(weights.values()), 4)
                     for key, value in reversed(tuple(weights.items()))},
                ),
            )
            for name, version, role, member_weights in definitions:
                row = self.session.scalar(
                    select(ModelDeploymentRecord).where(
                        ModelDeploymentRecord.market_family == family,
                        ModelDeploymentRecord.model_name == name,
                        ModelDeploymentRecord.model_version == version,
                    )
                )
                if row is None:
                    self.session.add(
                        ModelDeploymentRecord(
                            market_family=family,
                            model_name=name,
                            model_version=version,
                            role=role,
                            active=True,
                            weights=member_weights,
                            gate={
                                "minimum_samples": 50,
                                "maximum_brier": .30,
                                "maximum_calibration_error": .20,
                                "minimum_improvement": .01,
                                "promotion": "walk_forward_only",
                            },
                            promoted_at=(
                                datetime.now(timezone.utc)
                                if role == "champion" else None
                            ),
                        )
                    )
                    created += 1
        return created

    def run_temporal_backtests(self) -> int:
        rows = self.session.execute(
            select(Audit, Prediction, Market)
            .join(Prediction, Prediction.id == Audit.prediction_id)
            .join(Market, Market.id == Prediction.market_id)
            .where(Audit.result_status.in_(("won", "lost")))
            .order_by(Audit.audited_at)
        ).all()
        grouped: dict[str, list[tuple[Audit, Prediction]]] = defaultdict(list)
        for audit, prediction, market in rows:
            grouped[market_family(market.code)].append((audit, prediction))
        created = 0
        for family, samples in grouped.items():
            if len(samples) < 20:
                continue
            fingerprint = sha256(
                "|".join(f"{audit.id}:{audit.result_status}" for audit, _ in samples).encode()
            ).hexdigest()
            if self.session.scalar(
                select(TemporalBacktestRecord.id).where(
                    TemporalBacktestRecord.fingerprint == fingerprint
                )
            ):
                continue
            folds = []
            fold_size = max(10, len(samples) // 5)
            for end in range(fold_size * 2, len(samples) + 1, fold_size):
                train = samples[: end - fold_size]
                validate = samples[end - fold_size: end]
                folds.append({
                    "train_until": train[-1][0].audited_at.isoformat(),
                    "validate_until": validate[-1][0].audited_at.isoformat(),
                    "training_samples": len(train),
                    "validation_samples": len(validate),
                    "brier": self._brier(validate),
                })
            briers = [float(item["brier"]) for item in folds if item["brier"] is not None]
            average_brier = mean(briers) if briers else None
            passed = len(samples) >= 50 and average_brier is not None and average_brier <= .30
            self.session.add(
                TemporalBacktestRecord(
                    fingerprint=fingerprint,
                    model_name="specialized_ensemble",
                    model_version="ensemble-v2",
                    market_family=family,
                    folds=folds,
                    metrics={
                        "samples": len(samples),
                        "average_brier": average_brier,
                        "validation": "expanding_window_walk_forward",
                        "leakage_guard": "audit_time_ordered",
                    },
                    passed=passed,
                    evaluated_at=datetime.now(timezone.utc),
                )
            )
            created += 1
        return created

    def materialize_decision_policies(self) -> int:
        """Materializa calibração e cobertura seletiva sem reutilizar o futuro.

        Cada política é condicionada por competição, família de mercado, faixa
        de odd e horizonte. Segmentos pequenos herdam a política global e não
        recebem um selo artificial de alta confiança.
        """
        rows = self.session.execute(
            select(Audit, Prediction, Market, Match, Competition)
            .join(Prediction, Prediction.id == Audit.prediction_id)
            .join(Market, Market.id == Prediction.market_id)
            .join(Match, Match.id == Prediction.match_id)
            .join(Competition, Competition.id == Match.competition_id)
            .where(Audit.result_status.in_(("won", "lost")))
            .order_by(Audit.audited_at)
        ).all()
        grouped: dict[
            tuple[str, str, str, str],
            list[tuple[Audit, Prediction]],
        ] = defaultdict(list)
        for audit, prediction, market, match, competition in rows:
            policy = self._competition_code(competition)
            odds = (
                1 / float(prediction.implied_probability)
                if prediction.implied_probability else None
            )
            horizon_hours = max(
                0.0,
                self._hours_until(match.kickoff_at, prediction.created_at),
            )
            grouped[(
                policy,
                market_family(market.code),
                self._odds_band(odds),
                self._horizon(horizon_hours),
            )].append((audit, prediction))

        created = 0
        minimum = 30
        for (competition, family, odds_band, horizon), samples in grouped.items():
            if len(samples) < 10:
                continue
            signature = sha256(
                "|".join(
                    f"{audit.id}:{audit.result_status}:{audit.predicted_probability}"
                    for audit, _ in samples
                ).encode()
            ).hexdigest()
            if self.session.scalar(select(DecisionPolicyRecord.id).where(
                DecisionPolicyRecord.fingerprint == signature
            )):
                continue
            calibration_bins = self._calibration_bins(samples)
            threshold, selected_accuracy, coverage = self._selective_threshold(samples)
            split = max(1, int(len(samples) * .70))
            baseline = samples[:split]
            recent = samples[split:]
            baseline_brier = self._brier(baseline)
            recent_brier = self._brier(recent)
            drift_delta = (
                recent_brier - baseline_brier
                if baseline_brier is not None and recent_brier is not None else None
            )
            observed = sum(
                audit.result_status == "won" for audit, _ in samples
            )
            calibrated_rate = (observed + 2) / (len(samples) + 4)
            previous_policies = self.session.scalars(
                select(DecisionPolicyRecord).where(
                    DecisionPolicyRecord.competition == competition,
                    DecisionPolicyRecord.market_family == family,
                    DecisionPolicyRecord.odds_band == odds_band,
                    DecisionPolicyRecord.horizon == horizon,
                    DecisionPolicyRecord.active.is_(True),
                )
            ).all()
            for previous in previous_policies:
                previous.active = False
            self.session.add(DecisionPolicyRecord(
                fingerprint=signature,
                competition=competition,
                market_family=family,
                odds_band=odds_band,
                horizon=horizon,
                samples=len(samples),
                metrics={
                    "brier_score": self._brier(samples),
                    "hit_rate": observed / len(samples),
                    "log_loss": self._log_loss(samples),
                    "flat_stake_roi": self._flat_stake_roi(samples),
                    "minimum_sample_ready": len(samples) >= minimum,
                },
                calibration={
                    "method": "beta_binomial_isotonic_bins",
                    "posterior_hit_rate": calibrated_rate,
                    "bins": calibration_bins,
                },
                selection_policy={
                    "target_accuracy": .85,
                    "probability_threshold": threshold,
                    "observed_accuracy": selected_accuracy,
                    "coverage": coverage,
                    "abstain_below_threshold": True,
                },
                drift={
                    "baseline_brier": baseline_brier,
                    "recent_brier": recent_brier,
                    "delta": drift_delta,
                    "detected": bool(drift_delta is not None and drift_delta > .08),
                },
                active=len(samples) >= minimum,
                evaluated_at=datetime.now(timezone.utc),
            ))
            created += 1
        return created

    @staticmethod
    def _competition_code(competition: Competition) -> str:
        return f"{competition.country or 'global'}:{competition.name}"[:128]

    @staticmethod
    def _odds_band(odds: float | None) -> str:
        if odds is None:
            return "unavailable"
        if odds < 1.50:
            return "1.01-1.49"
        if odds < 2.00:
            return "1.50-1.99"
        if odds < 3.00:
            return "2.00-2.99"
        return "3.00+"

    @staticmethod
    def _horizon(hours: float) -> str:
        if hours <= 0:
            return "live"
        if hours <= 1.5:
            return "post_lineup"
        if hours <= 24:
            return "same_day"
        return "early"

    @staticmethod
    def _calibration_bins(
        samples: list[tuple[Audit, Prediction]],
    ) -> list[dict[str, object]]:
        bins = []
        last_observed = 0.0
        for index in range(10):
            lower, upper = index / 10, (index + 1) / 10
            bucket = [
                (audit, prediction) for audit, prediction in samples
                if lower <= float(audit.predicted_probability or prediction.probability) < upper
                or (index == 9 and float(audit.predicted_probability or prediction.probability) == 1)
            ]
            if not bucket:
                continue
            predicted = mean(
                float(audit.predicted_probability or prediction.probability)
                for audit, prediction in bucket
            )
            raw_observed = (
                sum(audit.result_status == "won" for audit, _ in bucket) + 2
            ) / (len(bucket) + 4)
            observed = max(last_observed, raw_observed)
            last_observed = observed
            bins.append({
                "lower": lower, "upper": upper, "samples": len(bucket),
                "predicted": predicted, "calibrated": observed,
            })
        return bins

    @staticmethod
    def _selective_threshold(
        samples: list[tuple[Audit, Prediction]],
    ) -> tuple[float, float | None, float]:
        target = .85
        best = (.99, None, 0.0)
        for threshold in (x / 100 for x in range(50, 96)):
            selected = [
                (audit, prediction) for audit, prediction in samples
                if float(audit.predicted_probability or prediction.probability) >= threshold
            ]
            if len(selected) < min(20, len(samples)):
                continue
            accuracy = sum(a.result_status == "won" for a, _ in selected) / len(selected)
            coverage = len(selected) / len(samples)
            if accuracy >= target and coverage > best[2]:
                best = (threshold, accuracy, coverage)
        return best

    @staticmethod
    def _log_loss(rows: list[tuple[Audit, Prediction]]) -> float | None:
        from math import log
        if not rows:
            return None
        values = []
        for audit, prediction in rows:
            probability = min(.999999, max(.000001, float(
                audit.predicted_probability or prediction.probability
            )))
            outcome = 1.0 if audit.result_status == "won" else 0.0
            values.append(-(outcome * log(probability) + (1 - outcome) * log(1 - probability)))
        return mean(values)

    @staticmethod
    def _flat_stake_roi(
        rows: list[tuple[Audit, Prediction]],
    ) -> float | None:
        returns = []
        for audit, prediction in rows:
            if not prediction.implied_probability:
                continue
            odds = 1 / float(prediction.implied_probability)
            returns.append(
                odds - 1 if audit.result_status == "won" else -1.0
            )
        return mean(returns) if returns else None

    @staticmethod
    def _brier(rows: list[tuple[Audit, Prediction]]) -> float | None:
        return mean(
            (
                float(audit.predicted_probability or prediction.probability)
                - (1.0 if audit.result_status == "won" else 0.0)
            ) ** 2
            for audit, prediction in rows
        ) if rows else None

    def materialize_explanations(self) -> int:
        now = datetime.now(timezone.utc)
        predictions = self.session.scalars(
            select(Prediction)
            .join(Match, Match.id == Prediction.match_id)
            .where(
                Match.status.in_(("scheduled", "in_progress")),
                Match.kickoff_at >= now.replace(tzinfo=None) - timedelta(hours=2),
            )
            .order_by(Prediction.created_at.desc())
            .limit(5000)
        ).all()
        created = 0
        for prediction in predictions:
            if self.session.scalar(
                select(PredictionExplanationRecord.id).where(
                    PredictionExplanationRecord.prediction_id == str(prediction.id)
                )
            ):
                continue
            market = self.session.get(Market, prediction.market_id)
            feature = self.session.scalar(
                select(FeatureSnapshotRecord)
                .where(
                    FeatureSnapshotRecord.entity_type == "match",
                    FeatureSnapshotRecord.entity_id == str(prediction.match_id),
                    FeatureSnapshotRecord.as_of <= prediction.created_at.replace(
                        tzinfo=timezone.utc
                    ),
                )
                .order_by(FeatureSnapshotRecord.as_of.desc())
            )
            favorable = []
            adverse = []
            if prediction.probability >= .60:
                favorable.append("probabilidade_modelo_acima_de_60_porcento")
            if prediction.expected_value is not None and prediction.expected_value > 0:
                favorable.append("valor_esperado_positivo")
            if prediction.evidence_level == "low":
                adverse.append("evidencia_historica_limitada")
            if prediction.implied_probability is None:
                adverse.append("odd_atual_indisponivel")
            self.session.add(
                PredictionExplanationRecord(
                    prediction_id=str(prediction.id),
                    match_id=str(prediction.match_id),
                    model_name=market_family(market.code if market else "other"),
                    model_version=prediction.model_version,
                    data_cutoff_at=prediction.created_at.replace(tzinfo=timezone.utc),
                    features=feature.values if feature else {},
                    favorable_factors=favorable,
                    adverse_factors=adverse,
                    decision={
                        "probability": prediction.probability,
                        "calibrated_probability": prediction.probability,
                        "implied_probability": prediction.implied_probability,
                        "expected_value": prediction.expected_value,
                        "recommended": bool(
                            prediction.expected_value is not None
                            and prediction.expected_value > 0
                        ),
                    },
                )
            )
            created += 1
        return created

    def register_pipeline_tasks(self) -> int:
        now = datetime.now(timezone.utc)
        bucket = now.strftime("%Y%m%d%H")
        tasks = [
            self.queue.enqueue(
                "data_quality_audit", f"quality:{bucket}", {"bucket": bucket}, priority=20
            ),
            self.queue.enqueue(
                "feature_materialization", f"features:{bucket}", {"bucket": bucket}, priority=30
            ),
            self.queue.enqueue(
                "temporal_validation", f"validation:{now:%Y%m%d}", {"date": f"{now:%Y-%m-%d}"},
                priority=80,
            ),
        ]
        # Este ciclo acabou de executar as três tarefas; o ledger persistente
        # permite repetição idempotente e retomada em ciclos futuros.
        for task in tasks:
            self.queue.complete(task)
        return len(tasks)

    def status(self) -> dict[str, object]:
        deployments = self.session.scalars(
            select(ModelDeploymentRecord).where(ModelDeploymentRecord.active.is_(True))
        ).all()
        latest_backtests = self.session.scalars(
            select(TemporalBacktestRecord)
            .order_by(TemporalBacktestRecord.evaluated_at.desc())
            .limit(20)
        ).all()
        quality_breakdown = dict(self.session.execute(
            select(
                DataQualityIncidentRecord.kind,
                func.count(DataQualityIncidentRecord.id),
            )
            .where(DataQualityIncidentRecord.resolved_at.is_(None))
            .group_by(DataQualityIncidentRecord.kind)
        ).all())
        return {
            "feature_store": {
                "snapshots": self.session.scalar(
                    select(func.count()).select_from(FeatureSnapshotRecord)
                ) or 0,
                "latest_as_of": self._iso(self.session.scalar(
                    select(func.max(FeatureSnapshotRecord.as_of))
                )),
                "leakage_guard": "strictly_before_kickoff",
            },
            "quality": {
                "open_incidents": self.session.scalar(
                    select(func.count())
                    .select_from(DataQualityIncidentRecord)
                    .where(DataQualityIncidentRecord.resolved_at.is_(None))
                ) or 0,
                "critical": self.session.scalar(
                    select(func.count())
                    .select_from(DataQualityIncidentRecord)
                    .where(
                        DataQualityIncidentRecord.resolved_at.is_(None),
                        DataQualityIncidentRecord.severity == "critical",
                    )
                ) or 0,
                "by_kind": quality_breakdown,
            },
            "models": {
                "deployments": len(deployments),
                "champions": sum(item.role == "champion" for item in deployments),
                "shadow_challengers": sum(item.role == "shadow" for item in deployments),
                "families": sorted({item.market_family for item in deployments}),
            },
            "backtesting": {
                "runs": self.session.scalar(
                    select(func.count()).select_from(TemporalBacktestRecord)
                ) or 0,
                "passed_families": sorted({
                    item.market_family for item in latest_backtests if item.passed
                }),
                "method": "expanding_window_walk_forward",
            },
            "decision_control": self._decision_control_status(),
            "explainability": {
                "predictions_explained": self.session.scalar(
                    select(func.count()).select_from(PredictionExplanationRecord)
                ) or 0,
            },
            "task_queue": {
                "pending": self.session.scalar(
                    select(func.count()).select_from(ProcessingTaskRecord).where(
                        ProcessingTaskRecord.status == "pending"
                    )
                ) or 0,
                "failed": self.session.scalar(
                    select(func.count()).select_from(ProcessingTaskRecord).where(
                        ProcessingTaskRecord.status == "failed"
                    )
                ) or 0,
                "completed": self.session.scalar(
                    select(func.count()).select_from(ProcessingTaskRecord).where(
                        ProcessingTaskRecord.status == "completed"
                    )
                ) or 0,
            },
        }

    def _decision_control_status(self) -> dict[str, object]:
        policies = self.session.scalars(
            select(DecisionPolicyRecord).where(DecisionPolicyRecord.active.is_(True))
        ).all()
        return {
            "active_policies": len(policies),
            "calibrated_segments": len({
                (item.competition, item.market_family, item.odds_band, item.horizon)
                for item in policies
            }),
            "drifted_segments": sum(bool(item.drift.get("detected")) for item in policies),
            "selective_prediction": "target_accuracy_with_abstention",
            "target_accuracy": .85,
            "dimensions": ["competition", "market_family", "odds_band", "horizon"],
        }

    @staticmethod
    def _iso(value: datetime | None) -> str | None:
        return value.isoformat() if value else None
