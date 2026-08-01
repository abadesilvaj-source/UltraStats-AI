"""add operational query indexes

Revision ID: d14a7c92b010
Revises: c92f8d31a009
"""

from collections.abc import Sequence

from alembic import op


revision: str = "d14a7c92b010"
down_revision: str | None = "c92f8d31a009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_matches_status_kickoff",
        "matches", ["status", "kickoff_at"], unique=False,
    )
    op.create_index(
        "ix_matches_home_status_kickoff",
        "matches", ["home_team_id", "status", "kickoff_at"], unique=False,
    )
    op.create_index(
        "ix_matches_away_status_kickoff",
        "matches", ["away_team_id", "status", "kickoff_at"], unique=False,
    )
    op.create_index(
        "ix_odds_match_collected_market",
        "odds", ["match_id", "collected_at", "market_id"], unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_odds_match_collected_market", table_name="odds")
    op.drop_index("ix_matches_away_status_kickoff", table_name="matches")
    op.drop_index("ix_matches_home_status_kickoff", table_name="matches")
    op.drop_index("ix_matches_status_kickoff", table_name="matches")
