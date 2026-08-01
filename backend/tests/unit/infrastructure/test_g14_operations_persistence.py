from datetime import datetime, timezone
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ultrastats_ai.domain.operations import QueueMessage, append_audit, create_backup
from ultrastats_ai.infrastructure.database.models import CanonicalBase
from ultrastats_ai.infrastructure.operations import OperationsStore


NOW = datetime.now(timezone.utc)


def test_metrics_alert_audit_backup_queue_and_queries() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            store = OperationsStore(session)
            metric = store.metric("latency", .2, {"route": "/health"}, NOW)
            alert = store.alert("high_latency", "warning", "Latency high", NOW)
            entry = append_audit((), "login", "user", NOW)[0]
            store.audit(entry)
            artifact = create_backup({"table": []}, NOW)
            backup = store.backup(artifact, "s3://bucket/backup")
            message = QueueMessage("message", {"job": "sync"})
            queued = store.enqueue("jobs", message, NOW)
            session.flush()
            assert store.enqueue("jobs", message, NOW) is queued
            assert store.verify_backup("missing", NOW) is False
            assert store.verify_backup(artifact.checksum, NOW) is True
            session.commit()
            assert store.open_alerts() == (alert,)
            assert store.latest_metrics() == (metric,)
            assert backup.status == "verified"
            with pytest.raises(ValueError, match="Limite"):
                store.latest_metrics(0)
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    ("method", "args", "message"),
    [
        ("metric", ("", 1, {}, NOW), "Métrica"),
        ("alert", ("", "warning", "message", NOW), "Alerta"),
        ("alert", ("code", "", "message", NOW), "Alerta"),
        ("alert", ("code", "warning", "", NOW), "Alerta"),
        ("backup", (create_backup({}, NOW), ""), "Backup"),
        ("enqueue", ("", QueueMessage("id", {}), NOW), "Fila"),
    ],
)
def test_store_validation(method, args, message) -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            with pytest.raises(ValueError, match=message):
                getattr(OperationsStore(session), method)(*args)
    finally:
        engine.dispose()


def test_empty_operational_queries() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            store = OperationsStore(session)
            assert store.open_alerts() == ()
            assert store.latest_metrics() == ()
    finally:
        engine.dispose()


def test_g14_migration_upgrade_and_downgrade() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "migrations"
        / "versions"
        / "a7e23594a440_create_production_operations.py"
    )
    spec = importlib.util.spec_from_file_location("g14_migration", path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    names = {
        "operational_metrics",
        "operational_alerts",
        "security_audit",
        "backup_catalog",
        "operational_queue",
    }
    try:
        with engine.begin() as connection:
            migration.op = Operations(MigrationContext.configure(connection))
            migration.upgrade()
            assert names <= set(connection.dialect.get_table_names(connection))
            migration.downgrade()
            assert names.isdisjoint(connection.dialect.get_table_names(connection))
    finally:
        engine.dispose()
