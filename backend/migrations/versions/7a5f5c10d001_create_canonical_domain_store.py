"""create canonical domain store

Revision ID: 7a5f5c10d001
Revises: 34f16155b3c2
Create Date: 2026-07-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7a5f5c10d001"
down_revision: Union[str, Sequence[str], None] = "34f16155b3c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "canonical_aggregates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("context", sa.String(length=64), nullable=False),
        sa.Column("aggregate_id", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("version > 0", name="ck_canonical_aggregate_version"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("context", "aggregate_id", name="uq_canonical_aggregate"),
    )
    op.create_index(
        "ix_canonical_aggregate_active",
        "canonical_aggregates",
        ["context", "deleted_at"],
    )
    op.create_table(
        "canonical_outbox",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_canonical_outbox_pending",
        "canonical_outbox",
        ["published_at", "occurred_at"],
    )
    op.create_table(
        "canonical_inbox",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("consumer", sa.String(length=255), nullable=False),
        sa.Column("message_id", sa.String(length=255), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("consumer", "message_id", name="uq_canonical_inbox"),
    )
    op.create_table(
        "canonical_audit_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("aggregate_record_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("actor", sa.String(length=255), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["aggregate_record_id"],
            ["canonical_aggregates.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("canonical_audit_log")
    op.drop_table("canonical_inbox")
    op.drop_index("ix_canonical_outbox_pending", table_name="canonical_outbox")
    op.drop_table("canonical_outbox")
    op.drop_index("ix_canonical_aggregate_active", table_name="canonical_aggregates")
    op.drop_table("canonical_aggregates")
