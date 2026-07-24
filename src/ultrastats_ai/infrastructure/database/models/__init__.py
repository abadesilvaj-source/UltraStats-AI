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
    "PredictiveForecastRecord",
    "PredictiveModelRecord",
]
