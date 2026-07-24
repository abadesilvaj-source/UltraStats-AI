from datetime import datetime, timezone
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.live import LiveEngine, LiveEvent, LiveEventType
from ultrastats_ai.infrastructure.database.models import CanonicalBase, LiveAnomalyRecord
from ultrastats_ai.infrastructure.live import LiveStore


NOW = datetime.now(timezone.utc)


def test_events_snapshots_effects_latest_recent_and_push() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            store = LiveStore(session)
            domain = LiveEngine()
            previous = domain.initial("match")
            first_event = LiveEvent(
                "score", "match", LiveEventType.SCORE, NOW, NOW, {"home": 1, "away": 0}
            )
            event_record = store.save_event(first_event)
            session.flush()
            assert store.save_event(first_event) is event_record
            current = domain.ingest(previous, first_event)
            first_snapshot = store.save_snapshot(current, NOW)
            store.record_effects(previous, current, first_event.event_id, NOW)
            regression_event = LiveEvent(
                "regression",
                "match",
                LiveEventType.SCORE,
                NOW,
                NOW,
                {"home": 0, "away": 0},
            )
            store.save_event(regression_event)
            blocked = domain.ingest(current, regression_event)
            second_snapshot = store.save_snapshot(blocked, NOW)
            store.record_effects(current, blocked, regression_event.event_id, NOW)
            session.commit()
            assert store.latest("match") is second_snapshot
            assert store.latest("missing") is None
            assert store.recent(1) == (first_snapshot,) or store.recent(1) == (second_snapshot,)
            assert session.scalar(select(LiveAnomalyRecord)).code == "score_regression"
            messages = [item.message for item in store.pending_push()]
            assert "goal:1-0" in messages
            assert "automatic_suspension" in messages
            with pytest.raises(ValueError, match="Limite"):
                store.recent(0)
    finally:
        engine.dispose()


def test_empty_queries_and_no_effects() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            store = LiveStore(session)
            state = LiveEngine.initial("match")
            store.record_effects(state, state, None, NOW)
            assert store.recent() == ()
            assert store.pending_push() == ()
    finally:
        engine.dispose()


def test_g13_migration_upgrade_and_downgrade() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "migrations"
        / "versions"
        / "f6d12483f339_create_live_engine.py"
    )
    spec = importlib.util.spec_from_file_location("g13_migration", path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    names = {"live_events", "live_snapshots", "live_anomalies", "live_push_deliveries"}
    try:
        with engine.begin() as connection:
            migration.op = Operations(MigrationContext.configure(connection))
            migration.upgrade()
            assert names <= set(connection.dialect.get_table_names(connection))
            migration.downgrade()
            assert names.isdisjoint(connection.dialect.get_table_names(connection))
    finally:
        engine.dispose()
