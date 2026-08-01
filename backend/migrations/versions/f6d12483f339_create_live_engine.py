"""create live engine

Revision ID: f6d12483f339
Revises: e5c01372e228
Create Date: 2026-07-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6d12483f339"
down_revision: Union[str, Sequence[str], None] = "e5c01372e228"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "live_events",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("match_id", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_live_event_match", "live_events", ["match_id", "occurred_at"])
    op.create_table(
        "live_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("match_id", sa.String(64), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("phase", sa.String(32), nullable=False),
        sa.Column("health", sa.String(32), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=False),
        sa.Column("away_score", sa.Integer(), nullable=False),
        sa.Column("statistics", sa.JSON(), nullable=False),
        sa.Column("odds", sa.JSON(), nullable=False),
        sa.Column("probabilities", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("anomalies", sa.JSON(), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "revision", name="uq_live_snapshot_revision"),
    )
    op.create_index("ix_live_snapshot_match", "live_snapshots", ["match_id", "revision"])
    op.create_table(
        "live_anomalies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("match_id", sa.String(64), nullable=False),
        sa.Column("event_id", sa.String(64)),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_live_anomaly_match", "live_anomalies", ["match_id", "detected_at"])
    op.create_table(
        "live_push_deliveries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("match_id", sa.String(64), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(255), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "revision", "message", name="uq_live_push_delivery"),
    )
    op.create_index("ix_live_push_pending", "live_push_deliveries", ["status", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_live_push_pending", table_name="live_push_deliveries")
    op.drop_table("live_push_deliveries")
    op.drop_index("ix_live_anomaly_match", table_name="live_anomalies")
    op.drop_table("live_anomalies")
    op.drop_index("ix_live_snapshot_match", table_name="live_snapshots")
    op.drop_table("live_snapshots")
    op.drop_index("ix_live_event_match", table_name="live_events")
    op.drop_table("live_events")
