"""create internal intelligence platform

Revision ID: e47c9a10b007
Revises: aa21f120d001
Create Date: 2026-07-30 18:45:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "e47c9a10b007"
down_revision: str | None = "aa21f120d001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "feature_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("feature_set", sa.String(64), nullable=False),
        sa.Column("values", sa.JSON(), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "entity_type", "entity_id", "feature_set", "as_of",
            name="uq_feature_snapshot_temporal",
        ),
    )
    op.create_index(
        "ix_feature_snapshot_lookup", "feature_snapshots",
        ["entity_type", "entity_id", "as_of"],
    )
    op.create_table(
        "data_quality_incidents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_data_quality_incident"),
    )
    op.create_index(
        "ix_data_quality_open", "data_quality_incidents",
        ["resolved_at", "severity"],
    )
    op.create_table(
        "model_deployments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("market_family", sa.String(64), nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("weights", sa.JSON(), nullable=False),
        sa.Column("gate", sa.JSON(), nullable=False),
        sa.Column("promoted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "market_family", "model_name", "model_version",
            name="uq_model_deployment",
        ),
    )
    op.create_index(
        "ix_model_deployment_active", "model_deployments",
        ["market_family", "role", "active"],
    )
    op.create_table(
        "temporal_backtests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("market_family", sa.String(64), nullable=False),
        sa.Column("folds", sa.JSON(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_temporal_backtest"),
    )
    op.create_index(
        "ix_temporal_backtest_market", "temporal_backtests",
        ["market_family", "evaluated_at"],
    )
    op.create_table(
        "processing_tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="uq_processing_task_key"),
    )
    op.create_index(
        "ix_processing_task_claim", "processing_tasks",
        ["status", "available_at", "priority"],
    )
    op.create_table(
        "prediction_explanations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("prediction_id", sa.String(64), nullable=False),
        sa.Column("match_id", sa.String(64), nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("data_cutoff_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("favorable_factors", sa.JSON(), nullable=False),
        sa.Column("adverse_factors", sa.JSON(), nullable=False),
        sa.Column("decision", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("prediction_id", name="uq_prediction_explanation"),
    )
    op.create_index(
        "ix_prediction_explanation_match", "prediction_explanations",
        ["match_id"],
    )


def downgrade() -> None:
    op.drop_table("prediction_explanations")
    op.drop_table("processing_tasks")
    op.drop_table("temporal_backtests")
    op.drop_table("model_deployments")
    op.drop_table("data_quality_incidents")
    op.drop_table("feature_snapshots")
