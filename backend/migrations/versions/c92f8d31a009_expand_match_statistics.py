"""expand match statistics

Revision ID: c92f8d31a009
Revises: f58d2b20c008
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "c92f8d31a009"
down_revision: str | None = "f58d2b20c008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


FIELDS = (
    "shots_off_target_home", "shots_off_target_away",
    "blocked_shots_home", "blocked_shots_away",
    "shots_inside_box_home", "shots_inside_box_away",
    "shots_outside_box_home", "shots_outside_box_away",
    "fouls_home", "fouls_away",
    "goalkeeper_saves_home", "goalkeeper_saves_away",
    "passes_home", "passes_away",
    "passes_accurate_home", "passes_accurate_away",
)


def upgrade() -> None:
    for field in FIELDS:
        op.add_column("match_statistics", sa.Column(field, sa.Integer(), nullable=True))
    op.add_column("match_statistics", sa.Column("pass_accuracy_home", sa.Float(), nullable=True))
    op.add_column("match_statistics", sa.Column("pass_accuracy_away", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("match_statistics", "pass_accuracy_away")
    op.drop_column("match_statistics", "pass_accuracy_home")
    for field in reversed(FIELDS):
        op.drop_column("match_statistics", field)
