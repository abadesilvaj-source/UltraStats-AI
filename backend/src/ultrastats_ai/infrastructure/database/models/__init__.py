"""Modelos SQLAlchemy da persistência canônica.

Os agregados são armazenados como snapshots versionados. O envelope mantém o
domínio desacoplado do ORM e permite evoluir cada contexto sem duplicar o
modelo legado existente em ``app``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CanonicalBase(DeclarativeBase):
    pass


class AggregateRecord(CanonicalBase):
    __tablename__ = "canonical_aggregates"
    __table_args__ = (
        UniqueConstraint("context", "aggregate_id", name="uq_canonical_aggregate"),
        CheckConstraint("version > 0", name="ck_canonical_aggregate_version"),
        Index("ix_canonical_aggregate_active", "context", "deleted_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    context: Mapped[str] = mapped_column(String(64), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    audit_entries: Mapped[list[AuditLogRecord]] = relationship(
        back_populates="aggregate", cascade="all, delete-orphan"
    )

    __mapper_args__ = {"version_id_col": version}


class OutboxMessage(CanonicalBase):
    __tablename__ = "canonical_outbox"
    __table_args__ = (Index("ix_canonical_outbox_pending", "published_at", "occurred_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class InboxMessage(CanonicalBase):
    __tablename__ = "canonical_inbox"
    __table_args__ = (UniqueConstraint("consumer", "message_id", name="uq_canonical_inbox"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    consumer: Mapped[str] = mapped_column(String(255), nullable=False)
    message_id: Mapped[str] = mapped_column(String(255), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditLogRecord(CanonicalBase):
    __tablename__ = "canonical_audit_log"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    aggregate_record_id: Mapped[UUID] = mapped_column(
        ForeignKey("canonical_aggregates.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    aggregate: Mapped[AggregateRecord] = relationship(back_populates="audit_entries")


class RawProviderPayloadRecord(CanonicalBase):
    __tablename__ = "provider_raw_payloads"
    __table_args__ = (
        UniqueConstraint("fingerprint", name="uq_provider_payload_fingerprint"),
        Index("ix_provider_payload_lookup", "provider", "resource", "collected_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    resource: Mapped[str] = mapped_column(String(64), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ProviderHealthRecord(CanonicalBase):
    __tablename__ = "provider_health_checks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class IdentityDecisionRecord(CanonicalBase):
    __tablename__ = "identity_decisions"
    __table_args__ = (
        UniqueConstraint("provider", "external_id", name="uq_identity_external"),
        Index("ix_identity_review_queue", "status", "decided_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    candidate_id: Mapped[str | None] = mapped_column(String(64))
    score: Mapped[str | None] = mapped_column(String(32))
    evidence: Mapped[dict[str, object] | None] = mapped_column(JSON)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    reviewer: Mapped[str | None] = mapped_column(String(255))
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FusionResultRecord(CanonicalBase):
    __tablename__ = "fusion_results"
    __table_args__ = (Index("ix_fusion_canonical", "canonical_id", "fused_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    canonical_id: Mapped[str] = mapped_column(String(64), nullable=False)
    values: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    provenance: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    conflicts: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    fused_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DataQuarantineRecord(CanonicalBase):
    __tablename__ = "data_quarantine"
    __table_args__ = (
        UniqueConstraint("payload_fingerprint", name="uq_quarantine_payload"),
        Index("ix_quarantine_pending", "resolved_at", "quarantined_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    resource: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    quarantined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class StatisticalSnapshotRecord(CanonicalBase):
    __tablename__ = "statistical_snapshots"
    __table_args__ = (
        UniqueConstraint("team_id", "reference_at", name="uq_statistical_snapshot"),
        Index("ix_statistical_snapshot_team", "team_id", "reference_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    team_id: Mapped[str] = mapped_column(String(64), nullable=False)
    reference_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    effective_sample_size: Mapped[str] = mapped_column(String(64), nullable=False)
    reliability: Mapped[str] = mapped_column(String(64), nullable=False)
    metrics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    distributions: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    trends: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    contexts: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class PredictiveModelRecord(CanonicalBase):
    __tablename__ = "predictive_models"
    __table_args__ = (
        UniqueConstraint("name", "version", "competition_id", "market", name="uq_predictive_model"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    competition_id: Mapped[str] = mapped_column(String(64), nullable=False)
    market: Mapped[str] = mapped_column(String(64), nullable=False)
    parameters: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class PredictiveForecastRecord(CanonicalBase):
    __tablename__ = "predictive_forecasts"
    __table_args__ = (
        UniqueConstraint("match_id", "model_name", "model_version", "market", name="uq_predictive_forecast"),
        Index("ix_predictive_forecast_match", "match_id", "generated_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    match_id: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    market: Mapped[str] = mapped_column(String(64), nullable=False)
    probabilities: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    explanations: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ModelBacktestRecord(CanonicalBase):
    __tablename__ = "model_backtests"
    __table_args__ = (Index("ix_model_backtest_model", "model_name", "model_version"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    samples: Mapped[int] = mapped_column(Integer, nullable=False)
    metrics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ProviderCapabilityRecord(CanonicalBase):
    __tablename__ = "provider_capabilities"
    __table_args__ = (
        UniqueConstraint("provider", "capability", name="uq_provider_capability"),
        Index("ix_provider_capability_status", "enabled", "provider"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    capability: Mapped[str] = mapped_column(String(64), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    terms_reference: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OddsSnapshotRecord(CanonicalBase):
    __tablename__ = "odds_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "match_id",
            "bookmaker",
            "market",
            "selection",
            "captured_at",
            name="uq_odds_snapshot",
        ),
        Index("ix_odds_snapshot_timeline", "match_id", "market", "captured_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    match_id: Mapped[str] = mapped_column(String(64), nullable=False)
    bookmaker: Mapped[str] = mapped_column(String(128), nullable=False)
    market: Mapped[str] = mapped_column(String(64), nullable=False)
    selection: Mapped[str] = mapped_column(String(128), nullable=False)
    decimal_odds: Mapped[str] = mapped_column(String(64), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TrainingDatasetRecord(CanonicalBase):
    __tablename__ = "training_datasets"
    __table_args__ = (UniqueConstraint("name", "version", name="uq_training_dataset"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    cutoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    samples: Mapped[int] = mapped_column(Integer, nullable=False)
    feature_schema: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    provider_coverage: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ModelValidationRecord(CanonicalBase):
    __tablename__ = "model_validations"
    __table_args__ = (
        UniqueConstraint("model_name", "model_version", "dataset_id", name="uq_model_validation"),
        Index("ix_model_validation_gate", "approved", "evaluated_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    dataset_id: Mapped[UUID] = mapped_column(
        ForeignKey("training_datasets.id", ondelete="RESTRICT"), nullable=False
    )
    metrics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    gate_failures: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RecommendationOpportunityRecord(CanonicalBase):
    __tablename__ = "recommendation_opportunities"
    __table_args__ = (
        UniqueConstraint("match_id", "market", "selection", "evaluated_at", name="uq_recommendation_snapshot"),
        Index("ix_recommendation_safe_score", "safe", "score"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    match_id: Mapped[str] = mapped_column(String(64), nullable=False)
    market: Mapped[str] = mapped_column(String(64), nullable=False)
    selection: Mapped[str] = mapped_column(String(128), nullable=False)
    bookmaker: Mapped[str | None] = mapped_column(String(128))
    offered_odds: Mapped[str | None] = mapped_column(String(64))
    metrics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    risk: Mapped[str] = mapped_column(String(32), nullable=False)
    score: Mapped[str] = mapped_column(String(64), nullable=False)
    safe: Mapped[bool] = mapped_column(Boolean, nullable=False)
    blocked_reasons: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    explanation: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    correlation_key: Mapped[str] = mapped_column(String(128), nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RecommendationAuditRecord(CanonicalBase):
    __tablename__ = "recommendation_audit"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    opportunity_id: Mapped[UUID] = mapped_column(
        ForeignKey("recommendation_opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FeatureSnapshotRecord(CanonicalBase):
    """Feature store temporal: somente dados conhecidos em ``as_of``."""

    __tablename__ = "feature_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "entity_type", "entity_id", "feature_set", "as_of",
            name="uq_feature_snapshot_temporal",
        ),
        Index("ix_feature_snapshot_lookup", "entity_type", "entity_id", "as_of"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    feature_set: Mapped[str] = mapped_column(String(64), nullable=False)
    values: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    provenance: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class DataQualityIncidentRecord(CanonicalBase):
    __tablename__ = "data_quality_incidents"
    __table_args__ = (
        UniqueConstraint("fingerprint", name="uq_data_quality_incident"),
        Index("ix_data_quality_open", "resolved_at", "severity"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ModelDeploymentRecord(CanonicalBase):
    __tablename__ = "model_deployments"
    __table_args__ = (
        UniqueConstraint(
            "market_family", "model_name", "model_version",
            name="uq_model_deployment",
        ),
        Index("ix_model_deployment_active", "market_family", "role", "active"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    market_family: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    weights: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    gate: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    promoted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class TemporalBacktestRecord(CanonicalBase):
    __tablename__ = "temporal_backtests"
    __table_args__ = (
        UniqueConstraint("fingerprint", name="uq_temporal_backtest"),
        Index("ix_temporal_backtest_market", "market_family", "evaluated_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    market_family: Mapped[str] = mapped_column(String(64), nullable=False)
    folds: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    metrics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ProcessingTaskRecord(CanonicalBase):
    """Fila persistente com chave idempotente e retomada após falha."""

    __tablename__ = "processing_tasks"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_processing_task_key"),
        Index("ix_processing_task_claim", "status", "available_at", "priority"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class PredictionExplanationRecord(CanonicalBase):
    __tablename__ = "prediction_explanations"
    __table_args__ = (
        UniqueConstraint("prediction_id", name="uq_prediction_explanation"),
        Index("ix_prediction_explanation_match", "match_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    prediction_id: Mapped[str] = mapped_column(String(64), nullable=False)
    match_id: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    data_cutoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    features: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    favorable_factors: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    adverse_factors: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    decision: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class DecisionPolicyRecord(CanonicalBase):
    """Política versionada de calibração, cobertura e risco por segmento."""

    __tablename__ = "decision_policies"
    __table_args__ = (
        UniqueConstraint("fingerprint", name="uq_decision_policy_fingerprint"),
        Index("ix_decision_policy_segment", "competition", "market_family", "evaluated_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    competition: Mapped[str] = mapped_column(String(128), nullable=False)
    market_family: Mapped[str] = mapped_column(String(64), nullable=False)
    odds_band: Mapped[str] = mapped_column(String(32), nullable=False)
    horizon: Mapped[str] = mapped_column(String(32), nullable=False)
    samples: Mapped[int] = mapped_column(Integer, nullable=False)
    metrics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    calibration: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    selection_policy: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    drift: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RiskProfileRecord(CanonicalBase):
    __tablename__ = "risk_profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uq_risk_profile_user"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    limits: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PortfolioSnapshotRecord(CanonicalBase):
    __tablename__ = "portfolio_snapshots"
    __table_args__ = (
        UniqueConstraint("user_id", "generated_at", name="uq_portfolio_snapshot"),
        Index("ix_portfolio_snapshot_user", "user_id", "generated_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    bankroll: Mapped[str] = mapped_column(String(64), nullable=False)
    total_exposure: Mapped[str] = mapped_column(String(64), nullable=False)
    positions: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    blocked: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    metrics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UserExperienceProfileRecord(CanonicalBase):
    __tablename__ = "user_experience_profiles"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    mode: Mapped[str] = mapped_column(String(16), nullable=False)
    locale: Mapped[str] = mapped_column(String(16), nullable=False)
    accessibility: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UserFavoriteRecord(CanonicalBase):
    __tablename__ = "user_favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "entity_type", "entity_id", name="uq_user_favorite"),
        Index("ix_user_favorite_user", "user_id", "entity_type"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UserAlertRecord(CanonicalBase):
    __tablename__ = "user_alerts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    metric: Mapped[str] = mapped_column(String(64), nullable=False)
    operator: Mapped[str] = mapped_column(String(4), nullable=False)
    threshold: Mapped[str] = mapped_column(String(64), nullable=False)
    channel: Mapped[str] = mapped_column(String(16), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class UserNotificationRecord(CanonicalBase):
    __tablename__ = "user_notifications"
    __table_args__ = (Index("ix_user_notification_feed", "user_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String(16), nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PushSubscriptionRecord(CanonicalBase):
    __tablename__ = "push_subscriptions"
    __table_args__ = (UniqueConstraint("user_id", "endpoint", name="uq_push_subscription"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    public_key: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AutomaticReportRecord(CanonicalBase):
    __tablename__ = "automatic_reports"
    __table_args__ = (Index("ix_automatic_report_user", "user_id", "generated_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LiveEventRecord(CanonicalBase):
    __tablename__ = "live_events"
    __table_args__ = (Index("ix_live_event_match", "match_id", "occurred_at"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    match_id: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LiveSnapshotRecord(CanonicalBase):
    __tablename__ = "live_snapshots"
    __table_args__ = (
        UniqueConstraint("match_id", "revision", name="uq_live_snapshot_revision"),
        Index("ix_live_snapshot_match", "match_id", "revision"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    match_id: Mapped[str] = mapped_column(String(64), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    phase: Mapped[str] = mapped_column(String(32), nullable=False)
    health: Mapped[str] = mapped_column(String(32), nullable=False)
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    home_score: Mapped[int] = mapped_column(Integer, nullable=False)
    away_score: Mapped[int] = mapped_column(Integer, nullable=False)
    statistics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    odds: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    probabilities: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    recommendations: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    anomalies: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LiveAnomalyRecord(CanonicalBase):
    __tablename__ = "live_anomalies"
    __table_args__ = (Index("ix_live_anomaly_match", "match_id", "detected_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    match_id: Mapped[str] = mapped_column(String(64), nullable=False)
    event_id: Mapped[str | None] = mapped_column(String(64))
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LivePushDeliveryRecord(CanonicalBase):
    __tablename__ = "live_push_deliveries"
    __table_args__ = (
        UniqueConstraint("match_id", "revision", "message", name="uq_live_push_delivery"),
        Index("ix_live_push_pending", "status", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    match_id: Mapped[str] = mapped_column(String(64), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OperationalMetricRecord(CanonicalBase):
    __tablename__ = "operational_metrics"
    __table_args__ = (Index("ix_operational_metric_name", "name", "recorded_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    value: Mapped[str] = mapped_column(String(64), nullable=False)
    labels: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OperationalAlertRecord(CanonicalBase):
    __tablename__ = "operational_alerts"
    __table_args__ = (Index("ix_operational_alert_status", "status", "created_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SecurityAuditRecord(CanonicalBase):
    __tablename__ = "security_audit"
    __table_args__ = (UniqueConstraint("sequence", name="uq_security_audit_sequence"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    entry_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class BackupCatalogRecord(CanonicalBase):
    __tablename__ = "backup_catalog"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OperationalQueueRecord(CanonicalBase):
    __tablename__ = "operational_queue"
    __table_args__ = (
        Index("ix_operational_queue_ready", "queue", "status", "available_at"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    queue: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


__all__ = [
    "AggregateRecord",
    "AuditLogRecord",
    "CanonicalBase",
    "InboxMessage",
    "OutboxMessage",
    "ProviderHealthRecord",
    "RawProviderPayloadRecord",
    "DataQuarantineRecord",
    "FusionResultRecord",
    "IdentityDecisionRecord",
    "StatisticalSnapshotRecord",
    "ModelBacktestRecord",
    "ProviderCapabilityRecord",
    "OddsSnapshotRecord",
    "TrainingDatasetRecord",
    "ModelValidationRecord",
    "PredictiveForecastRecord",
    "PredictiveModelRecord",
    "RecommendationAuditRecord",
    "RecommendationOpportunityRecord",
    "RiskProfileRecord",
    "PortfolioSnapshotRecord",
    "AutomaticReportRecord",
    "PushSubscriptionRecord",
    "UserAlertRecord",
    "UserExperienceProfileRecord",
    "UserFavoriteRecord",
    "UserNotificationRecord",
    "LiveAnomalyRecord",
    "LiveEventRecord",
    "LivePushDeliveryRecord",
    "LiveSnapshotRecord",
    "BackupCatalogRecord",
    "OperationalAlertRecord",
    "OperationalMetricRecord",
    "OperationalQueueRecord",
    "SecurityAuditRecord",
]
