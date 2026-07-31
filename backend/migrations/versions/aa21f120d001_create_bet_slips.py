"""create bet slips and legs

Revision ID: aa21f120d001
Revises: b8151a2c9e10
"""

from alembic import op
import sqlalchemy as sa

revision = "aa21f120d001"
down_revision = "b8151a2c9e10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bet_slips",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bankroll_id", sa.Integer(), nullable=False),
        sa.Column("bookmaker", sa.String(100), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("stake_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("total_odds", sa.Numeric(14, 4), nullable=False),
        sa.Column("potential_return", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("payout_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("placed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["bankroll_id"], ["bankrolls.id"]),
    )
    op.create_index("ix_bet_slips_bankroll_id", "bet_slips", ["bankroll_id"])
    op.create_index("ix_bet_slips_status", "bet_slips", ["status"])
    op.create_table(
        "bet_legs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slip_id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("market_id", sa.Integer(), nullable=False),
        sa.Column("prediction_id", sa.Integer(), nullable=True),
        sa.Column("selection", sa.String(150), nullable=False),
        sa.Column("odd_value", sa.Numeric(8, 3), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("result", sa.String(30), nullable=True),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["slip_id"], ["bet_slips.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["market_id"], ["markets.id"]),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.id"]),
    )
    op.create_index("ix_bet_legs_slip_id", "bet_legs", ["slip_id"])
    op.create_index("ix_bet_legs_match_id", "bet_legs", ["match_id"])
    with op.batch_alter_table("bankroll_transactions") as batch:
        batch.add_column(sa.Column("slip_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_bankroll_transactions_slip",
            "bet_slips",
            ["slip_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.create_index("ix_bankroll_transactions_slip_id", ["slip_id"])


def downgrade() -> None:
    with op.batch_alter_table("bankroll_transactions") as batch:
        batch.drop_index("ix_bankroll_transactions_slip_id")
        batch.drop_constraint("fk_bankroll_transactions_slip", type_="foreignkey")
        batch.drop_column("slip_id")
    op.drop_table("bet_legs")
    op.drop_table("bet_slips")
