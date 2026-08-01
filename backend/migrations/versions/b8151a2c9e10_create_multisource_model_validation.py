"""create multisource and model validation records

Revision ID: b8151a2c9e10
Revises: a7e23594a440
Create Date: 2026-07-24 19:30:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "b8151a2c9e10"
down_revision: str | None = "a7e23594a440"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "provider_capabilities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("capability", sa.String(64), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("terms_reference", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "capability", name="uq_provider_capability"),
    )
    op.create_index(
        "ix_provider_capability_status",
        "provider_capabilities",
        ["enabled", "provider"],
    )
    op.create_table(
        "odds_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("match_id", sa.String(64), nullable=False),
        sa.Column("bookmaker", sa.String(128), nullable=False),
        sa.Column("market", sa.String(64), nullable=False),
        sa.Column("selection", sa.String(128), nullable=False),
        sa.Column("decimal_odds", sa.String(64), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider",
            "match_id",
            "bookmaker",
            "market",
            "selection",
            "captured_at",
            name="uq_odds_snapshot",
        ),
    )
    op.create_index(
        "ix_odds_snapshot_timeline",
        "odds_snapshots",
        ["match_id", "market", "captured_at"],
    )
    op.create_table(
        "training_datasets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("version", sa.String(64), nullable=False),
        sa.Column("cutoff_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("samples", sa.Integer(), nullable=False),
        sa.Column("feature_schema", sa.JSON(), nullable=False),
        sa.Column("provider_coverage", sa.JSON(), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("checksum"),
        sa.UniqueConstraint("name", "version", name="uq_training_dataset"),
    )
    op.create_table(
        "model_validations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("gate_failures", sa.JSON(), nullable=False),
        sa.Column("approved", sa.Boolean(), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["training_datasets.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "model_name",
            "model_version",
            "dataset_id",
            name="uq_model_validation",
        ),
    )
    op.create_index(
        "ix_model_validation_gate",
        "model_validations",
        ["approved", "evaluated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_model_validation_gate", table_name="model_validations")
    op.drop_table("model_validations")
    op.drop_table("training_datasets")
    op.drop_index("ix_odds_snapshot_timeline", table_name="odds_snapshots")
    op.drop_table("odds_snapshots")
    op.drop_index("ix_provider_capability_status", table_name="provider_capabilities")
    op.drop_table("provider_capabilities")
