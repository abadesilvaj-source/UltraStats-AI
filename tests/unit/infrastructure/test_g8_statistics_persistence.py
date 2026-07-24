from datetime import datetime, timezone
from decimal import Decimal as D
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.statistics import Distribution, StatisticalSnapshot
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    StatisticalSnapshotRecord,
)
from ultrastats_ai.infrastructure.statistics import StatisticalSnapshotStore


NOW = datetime.now(timezone.utc)


def snapshot(reliability=D(".5")):
    return StatisticalSnapshot(
        "team",
        NOW,
        3,
        D("2.5"),
        reliability,
        {"form": D(".6")},
        {"goals": Distribution(D("1"), D(".2"), D("0"), D("2"))},
        {"goals": D(".1")},
        {"coach": D(".7")},
    )


def test_snapshot_store_upsert_and_latest() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            store = StatisticalSnapshotStore(session)
            assert store.latest("missing") is None
            store.save(snapshot())
            session.commit()
            store.save(snapshot(D(".8")))
            session.commit()
            assert len(session.scalars(select(StatisticalSnapshotRecord)).all()) == 1
            restored = store.latest("team")
            assert restored.reliability == D(".8")
            assert restored.distributions["goals"].variance == D(".2")
    finally:
        engine.dispose()


def test_g8_migration_upgrade_and_downgrade() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "migrations"
        / "versions"
        / "a18c8f40a004_create_statistical_snapshots.py"
    )
    spec = importlib.util.spec_from_file_location("g8_migration", path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            migration.op = Operations(MigrationContext.configure(connection))
            migration.upgrade()
            assert "statistical_snapshots" in connection.dialect.get_table_names(connection)
            migration.downgrade()
            assert "statistical_snapshots" not in connection.dialect.get_table_names(connection)
    finally:
        engine.dispose()
