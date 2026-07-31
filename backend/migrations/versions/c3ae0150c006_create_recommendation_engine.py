"""create recommendation engine

Revision ID: c3ae0150c006
Revises: b29d9040b005
Create Date: 2026-07-24
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c3ae0150c006"
down_revision: Union[str, Sequence[str], None] = "b29d9040b005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recommendation_opportunities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("match_id", sa.String(64), nullable=False),
        sa.Column("market", sa.String(64), nullable=False),
        sa.Column("selection", sa.String(128), nullable=False),
        sa.Column("bookmaker", sa.String(128)),
        sa.Column("offered_odds", sa.String(64)),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("risk", sa.String(32), nullable=False),
        sa.Column("score", sa.String(64), nullable=False),
        sa.Column("safe", sa.Boolean(), nullable=False),
        sa.Column("blocked_reasons", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.JSON(), nullable=False),
        sa.Column("correlation_key", sa.String(128), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "market", "selection", "evaluated_at", name="uq_recommendation_snapshot"),
    )
    op.create_index("ix_recommendation_safe_score", "recommendation_opportunities", ["safe", "score"])
    op.create_table(
        "recommendation_audit",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("actor", sa.String(255), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["opportunity_id"], ["recommendation_opportunities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("recommendation_audit")
    op.drop_index("ix_recommendation_safe_score", table_name="recommendation_opportunities")
    op.drop_table("recommendation_opportunities")
