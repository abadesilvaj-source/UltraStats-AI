from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import wraps
import logging
import os
import socket
import time
from typing import Callable, ParamSpec, TypeVar
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database.session import SessionLocal
from ultrastats_ai.infrastructure.database.models import ProcessingTaskRecord


P = ParamSpec("P")
R = TypeVar("R")
logger = logging.getLogger("ultrastats.scheduler.resilience")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _enabled(job_name: str) -> bool:
    value = os.getenv(f"JOB_{job_name.upper()}_ENABLED", "true")
    return value.strip().lower() in {"1", "true", "yes", "sim", "on"}


class ResilientJobService:
    """Lease persistente, retry e dead-letter para jobs idempotentes."""

    def __init__(self, job_name: str, *, maximum_runtime_seconds: int,
                 maximum_attempts: int = 3, slot_seconds: int = 30) -> None:
        if maximum_runtime_seconds <= 0 or maximum_attempts <= 0 or slot_seconds <= 0:
            raise ValueError("Limites do job resiliente devem ser positivos.")
        self.job_name = job_name
        self.maximum_runtime_seconds = maximum_runtime_seconds
        self.maximum_attempts = maximum_attempts
        self.slot_seconds = slot_seconds
        self.owner = f"{socket.gethostname()}:{os.getpid()}:{uuid4()}"

    def run(self, callback: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R | None:
        if not _enabled(self.job_name):
            logger.warning("Job %s desativado por kill switch.", self.job_name)
            return None
        task = self._claim()
        if task is None:
            logger.info("Job %s ignorado: lease ativo ou slot concluído.", self.job_name)
            return None
        started = time.monotonic()
        try:
            result = callback(*args, **kwargs)
        except Exception as error:
            self._finish(task.id, error=error, duration=time.monotonic() - started)
            logger.exception("Job resiliente %s falhou.", self.job_name)
            return None
        self._finish(task.id, error=None, duration=time.monotonic() - started)
        return result

    def _claim(self) -> ProcessingTaskRecord | None:
        now = _utcnow()
        with SessionLocal() as session:
            stale = session.scalars(
                select(ProcessingTaskRecord).where(
                    ProcessingTaskRecord.kind == f"scheduler:{self.job_name}",
                    ProcessingTaskRecord.status == "running",
                    ProcessingTaskRecord.locked_at < now - timedelta(seconds=self.maximum_runtime_seconds),
                ).with_for_update(skip_locked=True)
            ).all()
            for abandoned in stale:
                abandoned.status = "pending"
                abandoned.available_at = now
                abandoned.last_error = "lease expirado; retomada automática"
                abandoned.payload = {**(abandoned.payload or {}), "recovered_after_lease": True}
            if stale:
                session.flush()
            retry = session.scalar(
                select(ProcessingTaskRecord).where(
                    ProcessingTaskRecord.kind == f"scheduler:{self.job_name}",
                    ProcessingTaskRecord.status == "pending",
                    ProcessingTaskRecord.available_at <= now,
                ).order_by(ProcessingTaskRecord.priority, ProcessingTaskRecord.created_at)
                .with_for_update(skip_locked=True).limit(1)
            )
            if retry is not None:
                task = retry
            else:
                slot = int(now.timestamp()) // self.slot_seconds
                task = ProcessingTaskRecord(
                    kind=f"scheduler:{self.job_name}",
                    idempotency_key=f"scheduler:{self.job_name}:{slot}",
                    payload={"job": self.job_name, "slot": slot}, status="pending",
                    priority=10, attempts=0, max_attempts=self.maximum_attempts,
                    available_at=now, created_at=now,
                )
                session.add(task)
                try:
                    session.flush()
                except IntegrityError:
                    session.rollback()
                    return None
            if task.status == "running" and task.locked_at:
                locked_at = self._aware(task.locked_at)
                if locked_at + timedelta(seconds=self.maximum_runtime_seconds) > now:
                    return None
            task.status = "running"
            task.attempts += 1
            task.locked_at = now
            task.last_error = None
            task.payload = {
                **(task.payload or {}), "lease_owner": self.owner,
                "lease_expires_at": (now + timedelta(seconds=self.maximum_runtime_seconds)).isoformat(),
                "started_at": now.isoformat(),
            }
            session.commit()
            session.refresh(task)
            return task

    def _finish(self, task_id, *, error: Exception | None, duration: float) -> None:
        now = _utcnow()
        with SessionLocal() as session:
            task = session.get(ProcessingTaskRecord, task_id)
            if task is None:
                return
            timed_out = duration > self.maximum_runtime_seconds
            payload = {
                **(task.payload or {}), "finished_at": now.isoformat(),
                "duration_seconds": round(duration, 4), "timed_out": timed_out,
                "slo_seconds": self.maximum_runtime_seconds,
            }
            if error is None and not timed_out:
                task.status = "completed"
                task.finished_at = now
                task.last_error = None
                payload["outcome"] = "completed"
            else:
                message = (
                    f"soft timeout: {duration:.2f}s > {self.maximum_runtime_seconds}s"
                    if timed_out and error is None else f"{type(error).__name__}: {error}"
                )
                task.last_error = message[:4000]
                exhausted = task.attempts >= task.max_attempts
                task.status = "failed" if exhausted else "pending"
                task.available_at = now + timedelta(seconds=min(300, 2 ** task.attempts * 15))
                task.finished_at = now if exhausted else None
                payload["outcome"] = "dead_letter" if exhausted else "retry_scheduled"
                payload["dead_letter"] = exhausted
            task.payload = payload
            session.commit()

    @staticmethod
    def _aware(value: datetime) -> datetime:
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def resilient_job(job_name: str, *, maximum_runtime_seconds: int,
                  maximum_attempts: int = 3, slot_seconds: int = 30):
    def decorate(function: Callable[P, R]) -> Callable[P, R | None]:
        service = ResilientJobService(
            job_name, maximum_runtime_seconds=maximum_runtime_seconds,
            maximum_attempts=maximum_attempts, slot_seconds=slot_seconds,
        )

        @wraps(function)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R | None:
            return service.run(function, *args, **kwargs)

        return wrapped
    return decorate
