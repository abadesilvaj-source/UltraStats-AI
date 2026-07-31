"""link bets to bankroll

Revision ID: db33d016d6b4
Revises: 2fbd1f80d28b
Create Date: 2026-07-16 00:55:23.994280

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db33d016d6b4'
down_revision: Union[str, Sequence[str], None] = '2fbd1f80d28b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("bets") as batch:
        batch.add_column(sa.Column("bankroll_id", sa.Integer(), nullable=True))
        batch.add_column(
            sa.Column("stake_amount", sa.Numeric(precision=14, scale=2), nullable=True)
        )
        batch.add_column(
            sa.Column("payout_amount", sa.Numeric(precision=14, scale=2), nullable=True)
        )
        batch.create_index("ix_bets_bankroll_id", ["bankroll_id"], unique=False)
        batch.create_foreign_key(
            "fk_bets_bankroll_id_bankrolls",
            "bankrolls",
            ["bankroll_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("bets") as batch:
        batch.drop_constraint("fk_bets_bankroll_id_bankrolls", type_="foreignkey")
        batch.drop_index("ix_bets_bankroll_id")
        batch.drop_column("payout_amount")
        batch.drop_column("stake_amount")
        batch.drop_column("bankroll_id")
