"""Persistência operacional, de auditoria e recuperação."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.operations import AuditEntry, BackupArtifact, QueueMessage
from ultrastats_ai.infrastructure.database.models import (
    BackupCatalogRecord,
    OperationalAlertRecord,
    OperationalMetricRecord,
    OperationalQueueRecord,
    SecurityAuditRecord,
)


class OperationsStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def metric(
        self,
        name: str,
        value: float,
        labels: dict[str, object],
        recorded_at: datetime,
    ) -> OperationalMetricRecord:
        if not name.strip():
            raise ValueError("Métrica exige nome.")
        record = OperationalMetricRecord(
            name=name,
            value=str(value),
            labels=labels,
            recorded_at=recorded_at,
        )
        self.session.add(record)
        return record

    def alert(
        self,
        code: str,
        severity: str,
        message: str,
        created_at: datetime,
    ) -> OperationalAlertRecord:
        if not all(value.strip() for value in (code, severity, message)):
            raise ValueError("Alerta exige código, severidade e mensagem.")
        record = OperationalAlertRecord(
            code=code,
            severity=severity,
            message=message,
            status="open",
            created_at=created_at,
        )
        self.session.add(record)
        return record

    def audit(self, entry: AuditEntry) -> SecurityAuditRecord:
        record = SecurityAuditRecord(
            sequence=entry.sequence,
            action=entry.action,
            actor=entry.actor,
            previous_hash=entry.previous_hash,
            entry_hash=entry.hash,
            occurred_at=entry.occurred_at,
        )
        self.session.add(record)
        return record

    def backup(
        self,
        artifact: BackupArtifact,
        location: str,
    ) -> BackupCatalogRecord:
        if not location.strip():
            raise ValueError("Backup exige localização.")
        record = BackupCatalogRecord(
            checksum=artifact.checksum,
            size_bytes=len(artifact.payload),
            location=location,
            status="created",
            created_at=artifact.created_at,
        )
        self.session.add(record)
        return record

    def verify_backup(self, checksum: str, verified_at: datetime) -> bool:
        record = self.session.scalar(
            select(BackupCatalogRecord).where(BackupCatalogRecord.checksum == checksum)
        )
        if record is None:
            return False
        record.status = "verified"
        record.verified_at = verified_at
        return True

    def enqueue(
        self,
        queue: str,
        message: QueueMessage,
        available_at: datetime,
    ) -> OperationalQueueRecord:
        if not queue.strip():
            raise ValueError("Fila persistente exige nome.")
        existing = self.session.get(OperationalQueueRecord, message.message_id)
        if existing is not None:
            return existing
        record = OperationalQueueRecord(
            id=message.message_id,
            queue=queue,
            payload=dict(message.payload),
            status="ready",
            attempts=message.attempts,
            available_at=available_at,
        )
        self.session.add(record)
        return record

    def open_alerts(self) -> tuple[OperationalAlertRecord, ...]:
        return tuple(
            self.session.scalars(
                select(OperationalAlertRecord)
                .where(OperationalAlertRecord.status == "open")
                .order_by(OperationalAlertRecord.created_at.desc())
            ).all()
        )

    def latest_metrics(self, limit: int = 100) -> tuple[OperationalMetricRecord, ...]:
        if limit <= 0:
            raise ValueError("Limite de métricas deve ser positivo.")
        return tuple(
            self.session.scalars(
                select(OperationalMetricRecord)
                .order_by(OperationalMetricRecord.recorded_at.desc())
                .limit(limit)
            ).all()
        )
