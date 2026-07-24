"""Persistência idempotente de snapshots estatísticos."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.statistics import Distribution, StatisticalSnapshot
from ultrastats_ai.infrastructure.database.models import StatisticalSnapshotRecord


def _decimal_map(values):
    return {key: str(value) for key, value in values.items()}


class StatisticalSnapshotStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, snapshot: StatisticalSnapshot) -> None:
        record = self.session.scalar(
            select(StatisticalSnapshotRecord).where(
                StatisticalSnapshotRecord.team_id == snapshot.team_id,
                StatisticalSnapshotRecord.reference_at == snapshot.reference_at,
            )
        )
        if record is None:
            record = StatisticalSnapshotRecord(
                team_id=snapshot.team_id,
                reference_at=snapshot.reference_at,
                sample_size=snapshot.sample_size,
                effective_sample_size=str(snapshot.effective_sample_size),
                reliability=str(snapshot.reliability),
                metrics={},
                distributions={},
                trends={},
                contexts={},
            )
            self.session.add(record)
        record.sample_size = snapshot.sample_size
        record.effective_sample_size = str(snapshot.effective_sample_size)
        record.reliability = str(snapshot.reliability)
        record.metrics = _decimal_map(snapshot.metrics)
        record.distributions = {
            key: {
                "mean": str(value.mean),
                "variance": str(value.variance),
                "minimum": str(value.minimum),
                "maximum": str(value.maximum),
            }
            for key, value in snapshot.distributions.items()
        }
        record.trends = _decimal_map(snapshot.trends)
        record.contexts = _decimal_map(snapshot.contexts)

    def latest(self, team_id: str) -> StatisticalSnapshot | None:
        record = self.session.scalar(
            select(StatisticalSnapshotRecord)
            .where(StatisticalSnapshotRecord.team_id == team_id)
            .order_by(StatisticalSnapshotRecord.reference_at.desc())
            .limit(1)
        )
        if record is None:
            return None
        return StatisticalSnapshot(
            record.team_id,
            record.reference_at,
            record.sample_size,
            Decimal(record.effective_sample_size),
            Decimal(record.reliability),
            {key: Decimal(value) for key, value in record.metrics.items()},
            {
                key: Distribution(*(Decimal(data[field]) for field in ("mean", "variance", "minimum", "maximum")))
                for key, data in record.distributions.items()
            },
            {key: Decimal(value) for key, value in record.trends.items()},
            {key: Decimal(value) for key, value in record.contexts.items()},
        )
