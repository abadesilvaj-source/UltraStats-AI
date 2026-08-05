from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.temporal_ml_service import TemporalMLService
from ultrastats_ai.infrastructure.database.models import ProcessingTaskRecord


class ModelTrainingWorkerService:
    """Consome treino fora da inferencia e preserva o champion em falhas."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def run_once(self) -> dict[str, object]:
        now = datetime.now(timezone.utc)
        task = self.session.scalar(
            select(ProcessingTaskRecord).where(
                ProcessingTaskRecord.kind == "model_training",
                ProcessingTaskRecord.status == "pending",
                ProcessingTaskRecord.available_at <= now,
            ).order_by(ProcessingTaskRecord.priority, ProcessingTaskRecord.created_at)
            .with_for_update(skip_locked=True).limit(1)
        )
        if task is None:
            return {"processed": 0, "trained": False}
        task.status, task.locked_at, task.attempts = "running", now, task.attempts + 1
        self.session.commit()
        task_id = task.id
        try:
            TemporalMLService(self.session, force_retraining=True)._load_or_train()
            task = self.session.get(ProcessingTaskRecord, task_id)
            task.status, task.finished_at, task.locked_at = "completed", now, None
            task.payload = {**task.payload, "outcome": "completed", "finished_at": now.isoformat()}
            self.session.commit()
            return {"processed": 1, "trained": True}
        except Exception as error:
            self.session.rollback()
            task = self.session.get(ProcessingTaskRecord, task_id)
            task.last_error, task.locked_at = str(error)[:2000], None
            exhausted = task.attempts >= task.max_attempts
            task.status = "failed" if exhausted else "pending"
            task.finished_at = now if exhausted else None
            task.available_at = now + timedelta(minutes=min(60, 2 ** task.attempts))
            task.payload = {**task.payload, "dead_letter": exhausted}
            self.session.commit()
            raise
