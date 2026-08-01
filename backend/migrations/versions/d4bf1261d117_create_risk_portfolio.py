"""create risk and portfolio

Revision ID: d4bf1261d117
Revises: c3ae0150c006
Create Date: 2026-07-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4bf1261d117"
down_revision: Union[str, Sequence[str], None] = "c3ae0150c006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "risk_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("limits", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_risk_profile_user"),
    )
    op.create_table(
        "portfolio_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("bankroll", sa.String(64), nullable=False),
        sa.Column("total_exposure", sa.String(64), nullable=False),
        sa.Column("positions", sa.JSON(), nullable=False),
        sa.Column("blocked", sa.JSON(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "generated_at", name="uq_portfolio_snapshot"),
    )
    op.create_index(
        "ix_portfolio_snapshot_user",
        "portfolio_snapshots",
        ["user_id", "generated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_portfolio_snapshot_user", table_name="portfolio_snapshots")
    op.drop_table("portfolio_snapshots")
    op.drop_table("risk_profiles")
