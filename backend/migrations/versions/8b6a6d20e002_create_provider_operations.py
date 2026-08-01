"""create provider operations

Revision ID: 8b6a6d20e002
Revises: 7a5f5c10d001
Create Date: 2026-07-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8b6a6d20e002"
down_revision: Union[str, Sequence[str], None] = "7a5f5c10d001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "provider_raw_payloads",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("resource", sa.String(64), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_provider_payload_fingerprint"),
    )
    op.create_index(
        "ix_provider_payload_lookup",
        "provider_raw_payloads",
        ["provider", "resource", "collected_at"],
    )
    op.create_table(
        "provider_health_checks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(500), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_provider_health_checks_provider",
        "provider_health_checks",
        ["provider"],
    )


def downgrade() -> None:
    op.drop_index("ix_provider_health_checks_provider", table_name="provider_health_checks")
    op.drop_table("provider_health_checks")
    op.drop_index("ix_provider_payload_lookup", table_name="provider_raw_payloads")
    op.drop_table("provider_raw_payloads")
