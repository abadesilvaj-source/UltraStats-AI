"""create predictive registry

Revision ID: b29d9040b005
Revises: a18c8f40a004
Create Date: 2026-07-24
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b29d9040b005"
down_revision: Union[str, Sequence[str], None] = "a18c8f40a004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "predictive_models",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("version", sa.String(64), nullable=False),
        sa.Column("competition_id", sa.String(64), nullable=False),
        sa.Column("market", sa.String(64), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "version", "competition_id", "market", name="uq_predictive_model"),
    )
    op.create_table(
        "predictive_forecasts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("match_id", sa.String(64), nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("market", sa.String(64), nullable=False),
        sa.Column("probabilities", sa.JSON(), nullable=False),
        sa.Column("explanations", sa.JSON(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "model_name", "model_version", "market", name="uq_predictive_forecast"),
    )
    op.create_index("ix_predictive_forecast_match", "predictive_forecasts", ["match_id", "generated_at"])
    op.create_table(
        "model_backtests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("samples", sa.Integer(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_model_backtest_model", "model_backtests", ["model_name", "model_version"])


def downgrade() -> None:
    op.drop_index("ix_model_backtest_model", table_name="model_backtests")
    op.drop_table("model_backtests")
    op.drop_index("ix_predictive_forecast_match", table_name="predictive_forecasts")
    op.drop_table("predictive_forecasts")
    op.drop_table("predictive_models")
