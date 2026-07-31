"""create decision policies

Revision ID: f58d2b20c008
Revises: e47c9a10b007
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "f58d2b20c008"
down_revision: str | None = "e47c9a10b007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "decision_policies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("competition", sa.String(length=128), nullable=False),
        sa.Column("market_family", sa.String(length=64), nullable=False),
        sa.Column("odds_band", sa.String(length=32), nullable=False),
        sa.Column("horizon", sa.String(length=32), nullable=False),
        sa.Column("samples", sa.Integer(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("calibration", sa.JSON(), nullable=False),
        sa.Column("selection_policy", sa.JSON(), nullable=False),
        sa.Column("drift", sa.JSON(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_decision_policy_fingerprint"),
    )
    op.create_index(
        "ix_decision_policy_segment",
        "decision_policies",
        ["competition", "market_family", "evaluated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_decision_policy_segment", table_name="decision_policies")
    op.drop_table("decision_policies")
