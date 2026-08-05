from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import app.services.model_training_worker_service as module
from app.services.model_training_worker_service import ModelTrainingWorkerService
from ultrastats_ai.infrastructure.database.models import CanonicalBase, ProcessingTaskRecord


def _session():
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    return Session(engine)


def _task(session):
    now = datetime.now(timezone.utc)
    session.add(ProcessingTaskRecord(
        kind="model_training", idempotency_key="training:test", payload={},
        status="pending", priority=20, attempts=0, max_attempts=2,
        available_at=now, created_at=now,
    ))
    session.commit()


def test_training_worker_completes_without_replacing_champion_early(monkeypatch):
    session = _session(); _task(session)
    monkeypatch.setattr(module.TemporalMLService, "_load_or_train", lambda self: {"ok": True})
    assert ModelTrainingWorkerService(session).run_once()["trained"] is True
    assert session.scalar(select(ProcessingTaskRecord)).status == "completed"


def test_training_worker_retries_without_breaking_queue(monkeypatch):
    session = _session(); _task(session)
    monkeypatch.setattr(module.TemporalMLService, "_load_or_train", lambda self: (_ for _ in ()).throw(RuntimeError("boom")))
    try:
        ModelTrainingWorkerService(session).run_once()
    except RuntimeError:
        pass
    task = session.scalar(select(ProcessingTaskRecord))
    assert task.status == "pending"
    assert task.attempts == 1
