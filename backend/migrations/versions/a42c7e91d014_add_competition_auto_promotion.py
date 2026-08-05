"""add competition automatic promotion state

Revision ID: a42c7e91d014
Revises: f31a9d52c012
"""

import sqlalchemy as sa
from alembic import op


revision = "a42c7e91d014"
down_revision = "f31a9d52c012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("competitions") as batch:
        batch.add_column(sa.Column(
            "auto_core", sa.Boolean(), nullable=False,
            server_default=sa.false(),
        ))
        batch.add_column(sa.Column(
            "promotion_status", sa.String(30), nullable=False,
            server_default="observation",
        ))
        batch.add_column(sa.Column(
            "promotion_qualified_since", sa.DateTime(), nullable=True
        ))
        batch.add_column(sa.Column(
            "promotion_evaluated_at", sa.DateTime(), nullable=True
        ))
        batch.add_column(sa.Column(
            "promotion_metrics", sa.JSON(), nullable=False,
            server_default=sa.text("'{}'"),
        ))
        batch.create_index("ix_competitions_auto_core", ["auto_core"])


def downgrade() -> None:
    with op.batch_alter_table("competitions") as batch:
        batch.drop_index("ix_competitions_auto_core")
        batch.drop_column("promotion_metrics")
        batch.drop_column("promotion_evaluated_at")
        batch.drop_column("promotion_qualified_since")
        batch.drop_column("promotion_status")
        batch.drop_column("auto_core")
