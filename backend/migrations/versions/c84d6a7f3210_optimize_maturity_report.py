"""Optimize maturity dashboard report queries.

Revision ID: c84d6a7f3210
Revises: b53d8a44e015
"""

from alembic import op


revision = "c84d6a7f3210"
down_revision = "b53d8a44e015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS "
                "ix_odds_snapshot_captured ON odds_snapshots (captured_at)"
            )
            op.execute(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS "
                "ix_provider_payload_external_lookup ON provider_raw_payloads "
                "(provider, resource, external_id, collected_at)"
            )
            op.execute(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS "
                "ix_identity_candidate_status_provider ON identity_decisions "
                "(candidate_id, status, provider)"
            )
        return
    op.create_index(
        "ix_odds_snapshot_captured",
        "odds_snapshots",
        ["captured_at"],
        unique=False,
    )
    op.create_index(
        "ix_provider_payload_external_lookup",
        "provider_raw_payloads",
        ["provider", "resource", "external_id", "collected_at"],
        unique=False,
    )
    op.create_index(
        "ix_identity_candidate_status_provider",
        "identity_decisions",
        ["candidate_id", "status", "provider"],
        unique=False,
    )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_identity_candidate_status_provider")
            op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_provider_payload_external_lookup")
            op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_odds_snapshot_captured")
        return
    op.drop_index(
        "ix_identity_candidate_status_provider", table_name="identity_decisions"
    )
    op.drop_index(
        "ix_provider_payload_external_lookup", table_name="provider_raw_payloads"
    )
    op.drop_index("ix_odds_snapshot_captured", table_name="odds_snapshots")
