"""create statistical snapshots

Revision ID: a18c8f40a004
Revises: 9c7b7e30f003
Create Date: 2026-07-24
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a18c8f40a004"
down_revision: Union[str, Sequence[str], None] = "9c7b7e30f003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "statistical_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.String(64), nullable=False),
        sa.Column("reference_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("effective_sample_size", sa.String(64), nullable=False),
        sa.Column("reliability", sa.String(64), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("distributions", sa.JSON(), nullable=False),
        sa.Column("trends", sa.JSON(), nullable=False),
        sa.Column("contexts", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("team_id", "reference_at", name="uq_statistical_snapshot"),
    )
    op.create_index(
        "ix_statistical_snapshot_team",
        "statistical_snapshots",
        ["team_id", "reference_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_statistical_snapshot_team", table_name="statistical_snapshots")
    op.drop_table("statistical_snapshots")
