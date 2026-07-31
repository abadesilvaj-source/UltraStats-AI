"""Persistência append-only do Motor ao Vivo."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.live import LiveEvent, LiveMatchState
from ultrastats_ai.infrastructure.database.models import (
    LiveAnomalyRecord,
    LiveEventRecord,
    LivePushDeliveryRecord,
    LiveSnapshotRecord,
)


class LiveStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_event(self, event: LiveEvent) -> LiveEventRecord:
        existing = self.session.get(LiveEventRecord, event.event_id)
        if existing is not None:
            return existing
        record = LiveEventRecord(
            id=event.event_id,
            match_id=event.match_id,
            kind=event.kind.value,
            payload=dict(event.payload),
            occurred_at=event.occurred_at,
            received_at=event.received_at,
        )
        self.session.add(record)
        return record

    def save_snapshot(
        self,
        state: LiveMatchState,
        captured_at: datetime,
    ) -> LiveSnapshotRecord:
        record = LiveSnapshotRecord(
            match_id=state.match_id,
            revision=state.revision,
            phase=state.phase.value,
            health=state.health.value,
            minute=state.minute,
            home_score=state.home_score,
            away_score=state.away_score,
            statistics={key: str(value) for key, value in state.statistics.items()},
            odds={key: str(value) for key, value in state.odds.items()},
            probabilities={key: str(value) for key, value in state.probabilities.items()},
            recommendations=[
                {
                    "selection": item.selection,
                    "probability": str(item.probability),
                    "odds": str(item.odds),
                    "expected_value": str(item.expected_value),
                }
                for item in state.recommendations
            ],
            anomalies=list(state.anomalies),
            captured_at=captured_at,
        )
        self.session.add(record)
        return record

    def record_effects(
        self,
        previous: LiveMatchState,
        current: LiveMatchState,
        event_id: str | None,
        detected_at: datetime,
    ) -> None:
        for code in current.anomalies[len(previous.anomalies) :]:
            self.session.add(
                LiveAnomalyRecord(
                    match_id=current.match_id,
                    event_id=event_id,
                    code=code,
                    detected_at=detected_at,
                )
            )
        for message in current.push_messages[len(previous.push_messages) :]:
            self.session.add(
                LivePushDeliveryRecord(
                    match_id=current.match_id,
                    revision=current.revision,
                    message=message,
                    status="pending",
                    created_at=detected_at,
                )
            )

    def latest(self, match_id: str) -> LiveSnapshotRecord | None:
        return self.session.scalar(
            select(LiveSnapshotRecord)
            .where(LiveSnapshotRecord.match_id == match_id)
            .order_by(LiveSnapshotRecord.revision.desc())
            .limit(1)
        )

    def recent(self, limit: int = 50) -> tuple[LiveSnapshotRecord, ...]:
        if limit <= 0:
            raise ValueError("Limite deve ser positivo.")
        return tuple(
            self.session.scalars(
                select(LiveSnapshotRecord)
                .order_by(LiveSnapshotRecord.captured_at.desc())
                .limit(limit)
            ).all()
        )

    def pending_push(self) -> tuple[LivePushDeliveryRecord, ...]:
        return tuple(
            self.session.scalars(
                select(LivePushDeliveryRecord)
                .where(LivePushDeliveryRecord.status == "pending")
                .order_by(LivePushDeliveryRecord.created_at)
            ).all()
        )
