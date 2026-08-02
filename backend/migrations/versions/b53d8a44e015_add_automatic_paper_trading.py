"""add automatic paper trading and learning

Revision ID: b53d8a44e015
Revises: a42c7e91d014
"""

import sqlalchemy as sa
from alembic import op

revision = "b53d8a44e015"
down_revision = "a42c7e91d014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "paper_portfolios",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("initial_balance", sa.Float(), nullable=False),
        sa.Column("current_balance", sa.Float(), nullable=False),
        sa.Column("peak_balance", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(8), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "paper_bets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("portfolio_id", sa.Uuid(), sa.ForeignKey("paper_portfolios.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("opportunity_id", sa.Uuid(), sa.ForeignKey("recommendation_opportunities.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("match_id", sa.String(64), nullable=False),
        sa.Column("competition_id", sa.String(64)),
        sa.Column("market", sa.String(64), nullable=False),
        sa.Column("selection", sa.String(128), nullable=False),
        sa.Column("risk", sa.String(32), nullable=False),
        sa.Column("offered_odds", sa.Float(), nullable=False),
        sa.Column("closing_odds", sa.Float()),
        sa.Column("probability", sa.Float(), nullable=False),
        sa.Column("stake", sa.Float(), nullable=False),
        sa.Column("payout", sa.Float(), nullable=False, server_default="0"),
        sa.Column("profit", sa.Float(), nullable=False, server_default="0"),
        sa.Column("clv", sa.Float()),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("recommended_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("kickoff_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("settled_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("opportunity_id", name="uq_paper_bet_opportunity"),
    )
    op.create_index("ix_paper_bet_settlement", "paper_bets", ["status", "match_id"])
    op.create_index("ix_paper_bet_segment", "paper_bets", ["competition_id", "market", "settled_at"])
    op.create_table(
        "paper_learning_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("policy_updates", sa.JSON(), nullable=False),
        sa.Column("model_training_triggered", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("paper_learning_runs")
    op.drop_index("ix_paper_bet_segment", table_name="paper_bets")
    op.drop_index("ix_paper_bet_settlement", table_name="paper_bets")
    op.drop_table("paper_bets")
    op.drop_table("paper_portfolios")
