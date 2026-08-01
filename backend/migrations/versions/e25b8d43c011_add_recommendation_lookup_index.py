"""add recommendation dashboard lookup index

Revision ID: e25b8d43c011
Revises: d14a7c92b010
"""

from alembic import op


revision = "e25b8d43c011"
down_revision = "d14a7c92b010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_recommendation_evaluated_match_safe",
        "recommendation_opportunities",
        ["evaluated_at", "match_id", "safe"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_recommendation_evaluated_match_safe",
        table_name="recommendation_opportunities",
    )
