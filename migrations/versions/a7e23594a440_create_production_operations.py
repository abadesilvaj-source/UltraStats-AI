"""create production operations

Revision ID: a7e23594a440
Revises: f6d12483f339
Create Date: 2026-07-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7e23594a440"
down_revision: Union[str, Sequence[str], None] = "f6d12483f339"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "operational_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("value", sa.String(64), nullable=False),
        sa.Column("labels", sa.JSON(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_operational_metric_name",
        "operational_metrics",
        ["name", "recorded_at"],
    )
    op.create_table(
        "operational_alerts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(128), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_operational_alert_status",
        "operational_alerts",
        ["status", "created_at"],
    )
    op.create_table(
        "security_audit",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("actor", sa.String(128), nullable=False),
        sa.Column("previous_hash", sa.String(64), nullable=False),
        sa.Column("entry_hash", sa.String(64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sequence", name="uq_security_audit_sequence"),
    )
    op.create_table(
        "backup_catalog",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("location", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("checksum"),
    )
    op.create_table(
        "operational_queue",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("queue", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_operational_queue_ready",
        "operational_queue",
        ["queue", "status", "available_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_operational_queue_ready", table_name="operational_queue")
    op.drop_table("operational_queue")
    op.drop_table("backup_catalog")
    op.drop_table("security_audit")
    op.drop_index("ix_operational_alert_status", table_name="operational_alerts")
    op.drop_table("operational_alerts")
    op.drop_index("ix_operational_metric_name", table_name="operational_metrics")
    op.drop_table("operational_metrics")
