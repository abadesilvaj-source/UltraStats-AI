"""Repository SQLAlchemy genérico para Aggregate Roots canônicos."""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from ultrastats_ai.infrastructure.database.models import AggregateRecord

Aggregate = TypeVar("Aggregate")


class SqlAlchemyAggregateRepository(Generic[Aggregate]):
    def __init__(
        self,
        session: Session,
        context: str,
        serializer: Callable[[Aggregate], dict[str, object]],
        deserializer: Callable[[dict[str, object]], Aggregate],
        id_getter: Callable[[Aggregate], object] = lambda aggregate: aggregate.id,
    ) -> None:
        self.session = session
        self.context = context
        self.serializer = serializer
        self.deserializer = deserializer
        self.id_getter = id_getter

    def get_by_id(self, aggregate_id: object) -> Aggregate | None:
        record = self.session.scalar(
            select(AggregateRecord).where(
                AggregateRecord.context == self.context,
                AggregateRecord.aggregate_id == str(aggregate_id),
                AggregateRecord.deleted_at.is_(None),
            )
        )
        return None if record is None else self.deserializer(record.payload)

    def add(self, aggregate: Aggregate) -> None:
        self.session.add(
            AggregateRecord(
                context=self.context,
                aggregate_id=str(self.id_getter(aggregate)),
                payload=self.serializer(aggregate),
            )
        )

    def save(self, aggregate: Aggregate) -> None:
        record = self._required(self.id_getter(aggregate))
        record.payload = self.serializer(aggregate)

    def remove(self, aggregate: Aggregate) -> None:
        from datetime import datetime, timezone

        self._required(self.id_getter(aggregate)).deleted_at = datetime.now(timezone.utc)

    def _required(self, aggregate_id: object) -> AggregateRecord:
        record = self.session.scalar(
            select(AggregateRecord).where(
                AggregateRecord.context == self.context,
                AggregateRecord.aggregate_id == str(aggregate_id),
                AggregateRecord.deleted_at.is_(None),
            )
        )
        if record is None:
            raise LookupError(f"Agregado {aggregate_id!s} não encontrado.")
        return record


__all__ = ["SqlAlchemyAggregateRepository"]
