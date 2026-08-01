"""add user authentication and private bankroll ownership

Revision ID: f31a9d52c012
Revises: e25b8d43c011
"""

import sqlalchemy as sa
from alembic import op


revision = "f31a9d52c012"
down_revision = "e25b8d43c011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # O produto passa a iniciar uma nova área pessoal por conta.
    op.execute("DELETE FROM bankroll_transactions")
    op.execute("DELETE FROM bet_legs")
    op.execute("DELETE FROM bet_slips")
    op.execute("DELETE FROM bets")
    op.execute("DELETE FROM bankrolls")
    op.execute("DELETE FROM user_favorites")

    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.drop_index("ix_bankrolls_name", table_name="bankrolls")
    with op.batch_alter_table("bankrolls") as batch:
        batch.add_column(sa.Column("user_id", sa.String(36), nullable=False))
        batch.create_foreign_key(
            "fk_bankrolls_user_id_users", "users", ["user_id"], ["id"],
            ondelete="CASCADE",
        )
        batch.create_index("ix_bankrolls_user_id", ["user_id"])
        batch.create_unique_constraint(
            "uq_bankrolls_user_name", ["user_id", "name"]
        )
    op.create_index("ix_bankrolls_name", "bankrolls", ["name"], unique=False)


def downgrade() -> None:
    op.execute("DELETE FROM bankroll_transactions")
    op.execute("DELETE FROM bet_legs")
    op.execute("DELETE FROM bet_slips")
    op.execute("DELETE FROM bankrolls")
    op.drop_index("ix_bankrolls_name", table_name="bankrolls")
    with op.batch_alter_table("bankrolls") as batch:
        batch.drop_constraint("uq_bankrolls_user_name", type_="unique")
        batch.drop_index("ix_bankrolls_user_id")
        batch.drop_constraint("fk_bankrolls_user_id_users", type_="foreignkey")
        batch.drop_column("user_id")
    op.create_index("ix_bankrolls_name", "bankrolls", ["name"], unique=True)
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
