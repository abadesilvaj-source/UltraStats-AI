from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
import pytest

import app.services.resilient_job_service as module
from app.services.resilient_job_service import ResilientJobService
from ultrastats_ai.infrastructure.database.models import CanonicalBase, ProcessingTaskRecord


def _database(monkeypatch):
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    monkeypatch.setattr(module, "SessionLocal", factory)
    return factory


def test_completed_job_is_persisted_and_same_slot_is_idempotent(monkeypatch):
    factory = _database(monkeypatch)
    service = ResilientJobService("test", maximum_runtime_seconds=30, slot_seconds=3600)
    calls = []

    assert service.run(lambda: calls.append("ok") or 7) == 7
    assert service.run(lambda: calls.append("duplicate")) is None

    with factory() as session:
        task = session.scalar(select(ProcessingTaskRecord))
        assert task.status == "completed"
        assert task.payload["outcome"] == "completed"
        assert task.payload["duration_seconds"] >= 0
    assert calls == ["ok"]


def test_failure_retries_and_reaches_dead_letter(monkeypatch):
    factory = _database(monkeypatch)
    service = ResilientJobService(
        "retry", maximum_runtime_seconds=30, maximum_attempts=2, slot_seconds=3600
    )

    service.run(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    with factory() as session:
        task = session.scalar(select(ProcessingTaskRecord))
        assert task.status == "pending"
        task.available_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        session.commit()

    service.run(lambda: (_ for _ in ()).throw(RuntimeError("boom again")))
    with factory() as session:
        task = session.scalar(select(ProcessingTaskRecord))
        assert task.status == "failed"
        assert task.payload["dead_letter"] is True
        assert task.attempts == 2


def test_kill_switch_prevents_claim(monkeypatch):
    factory = _database(monkeypatch)
    monkeypatch.setenv("JOB_DISABLED_ENABLED", "false")
    service = ResilientJobService("disabled", maximum_runtime_seconds=30)

    assert service.run(lambda: 1) is None
    with factory() as session:
        assert session.scalar(select(ProcessingTaskRecord)) is None


@pytest.mark.parametrize("job_name", [
    "sync", "live", "backfill", "odds", "paper", "training"
])
def test_expired_lease_is_recovered_for_every_job(monkeypatch, job_name):
    factory = _database(monkeypatch)
    now = datetime.now(timezone.utc)
    with factory() as session:
        session.add(ProcessingTaskRecord(
            kind=f"scheduler:{job_name}", idempotency_key=f"scheduler:{job_name}:old",
            payload={}, status="running", priority=10, attempts=1, max_attempts=3,
            available_at=now, locked_at=now - timedelta(minutes=5), created_at=now,
        ))
        session.commit()
    service = ResilientJobService(job_name, maximum_runtime_seconds=30)

    assert service.run(lambda: "recovered") == "recovered"
    with factory() as session:
        task = session.scalar(select(ProcessingTaskRecord))
        assert task.status == "completed"
        assert task.payload["recovered_after_lease"] is True
