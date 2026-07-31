"""create identity fusion workflow

Revision ID: 9c7b7e30f003
Revises: 8b6a6d20e002
Create Date: 2026-07-24
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "9c7b7e30f003"
down_revision: Union[str, Sequence[str], None] = "8b6a6d20e002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "identity_decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("candidate_id", sa.String(64)),
        sa.Column("score", sa.String(32)),
        sa.Column("evidence", sa.JSON()),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("reviewer", sa.String(255)),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "external_id", name="uq_identity_external"),
    )
    op.create_index("ix_identity_review_queue", "identity_decisions", ["status", "decided_at"])
    op.create_table(
        "fusion_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("canonical_id", sa.String(64), nullable=False),
        sa.Column("values", sa.JSON(), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
        sa.Column("conflicts", sa.JSON(), nullable=False),
        sa.Column("fused_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fusion_canonical", "fusion_results", ["canonical_id", "fused_at"])
    op.create_table(
        "data_quarantine",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("resource", sa.String(64), nullable=False),
        sa.Column("payload_fingerprint", sa.String(64), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("quarantined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payload_fingerprint", name="uq_quarantine_payload"),
    )
    op.create_index("ix_quarantine_pending", "data_quarantine", ["resolved_at", "quarantined_at"])


def downgrade() -> None:
    op.drop_index("ix_quarantine_pending", table_name="data_quarantine")
    op.drop_table("data_quarantine")
    op.drop_index("ix_fusion_canonical", table_name="fusion_results")
    op.drop_table("fusion_results")
    op.drop_index("ix_identity_review_queue", table_name="identity_decisions")
    op.drop_table("identity_decisions")
