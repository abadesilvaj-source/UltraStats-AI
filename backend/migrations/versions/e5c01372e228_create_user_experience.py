"""create user experience

Revision ID: e5c01372e228
Revises: d4bf1261d117
Create Date: 2026-07-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5c01372e228"
down_revision: Union[str, Sequence[str], None] = "d4bf1261d117"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_experience_profiles",
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("mode", sa.String(16), nullable=False),
        sa.Column("locale", sa.String(16), nullable=False),
        sa.Column("accessibility", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_table(
        "user_favorites",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "entity_type", "entity_id", name="uq_user_favorite"),
    )
    op.create_index("ix_user_favorite_user", "user_favorites", ["user_id", "entity_type"])
    op.create_table(
        "user_alerts",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("metric", sa.String(64), nullable=False),
        sa.Column("operator", sa.String(4), nullable=False),
        sa.Column("threshold", sa.String(64), nullable=False),
        sa.Column("channel", sa.String(16), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_alerts_user_id", "user_alerts", ["user_id"])
    op.create_table(
        "user_notifications",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("channel", sa.String(16), nullable=False),
        sa.Column("read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_notification_feed",
        "user_notifications",
        ["user_id", "created_at"],
    )
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("public_key", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "endpoint", name="uq_push_subscription"),
    )
    op.create_table(
        "automatic_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_automatic_report_user",
        "automatic_reports",
        ["user_id", "generated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_automatic_report_user", table_name="automatic_reports")
    op.drop_table("automatic_reports")
    op.drop_table("push_subscriptions")
    op.drop_index("ix_user_notification_feed", table_name="user_notifications")
    op.drop_table("user_notifications")
    op.drop_index("ix_user_alerts_user_id", table_name="user_alerts")
    op.drop_table("user_alerts")
    op.drop_index("ix_user_favorite_user", table_name="user_favorites")
    op.drop_table("user_favorites")
    op.drop_table("user_experience_profiles")
