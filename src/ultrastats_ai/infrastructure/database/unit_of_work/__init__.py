"""Unit of Work SQLAlchemy com Outbox transacional."""

from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session

from ultrastats_ai.application.ports.unit_of_work import UnitOfWork
from ultrastats_ai.infrastructure.database.models import OutboxMessage


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self.session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self) -> Self:
        self.session = self.session_factory()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        return super().__exit__(exception_type, exception, traceback)

    def enqueue(self, event_type: str, payload: dict[str, object]) -> None:
        self._session().add(OutboxMessage(event_type=event_type, payload=payload))

    def commit(self) -> None:
        self._session().commit()

    def rollback(self) -> None:
        self._session().rollback()

    def close(self) -> None:
        if self.session is not None:
            self.session.close()
            self.session = None

    def _session(self) -> Session:
        if self.session is None:
            raise RuntimeError("Unit of Work deve estar dentro de um context manager.")
        return self.session


__all__ = ["SqlAlchemyUnitOfWork"]
