from dataclasses import dataclass
from datetime import datetime
import importlib.util
from pathlib import Path
from uuid import UUID

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from ultrastats_ai.infrastructure.database import (
    CanonicalBase,
    SqlAlchemyAggregateRepository,
    SqlAlchemyUnitOfWork,
)
from ultrastats_ai.infrastructure.database.models import (
    AggregateRecord,
    AuditLogRecord,
    InboxMessage,
    OutboxMessage,
)


@dataclass
class Sample:
    id: str
    value: int


def _repository(session: Session) -> SqlAlchemyAggregateRepository[Sample]:
    return SqlAlchemyAggregateRepository(
        session,
        "sample",
        lambda aggregate: {"id": aggregate.id, "value": aggregate.value},
        lambda payload: Sample(str(payload["id"]), int(payload["value"])),
    )


@pytest.fixture
def factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    yield sessionmaker(engine, expire_on_commit=False)
    engine.dispose()


def test_repository_lifecycle_and_soft_delete(factory: sessionmaker[Session]) -> None:
    with factory() as session:
        repository = _repository(session)
        assert repository.get_by_id("missing") is None
        item = Sample("one", 1)
        repository.add(item)
        session.commit()
        assert repository.get_by_id("one") == item
        item.value = 2
        repository.save(item)
        session.commit()
        assert repository.get_by_id("one") == item
        repository.remove(item)
        session.commit()
        assert repository.get_by_id("one") is None
        with pytest.raises(LookupError):
            repository.save(item)


def test_models_constraints_relationships_and_defaults(factory: sessionmaker[Session]) -> None:
    with factory() as session:
        aggregate = AggregateRecord(context="team", aggregate_id="1", payload={})
        aggregate.audit_entries.append(AuditLogRecord(action="created", actor="test"))
        inbox = InboxMessage(consumer="worker", message_id="event-1")
        outbox = OutboxMessage(event_type="TeamCreated", payload={"id": "1"})
        session.add_all((aggregate, inbox, outbox))
        session.commit()
        assert isinstance(aggregate.id, UUID)
        assert isinstance(aggregate.created_at, datetime)
        assert aggregate.audit_entries[0].aggregate is aggregate
        assert inbox.received_at is not None
        assert outbox.occurred_at is not None
        session.add(InboxMessage(consumer="worker", message_id="event-1"))
        with pytest.raises(IntegrityError):
            session.commit()


def test_unit_of_work_commit_rollback_close_and_guard(factory: sessionmaker[Session]) -> None:
    unit = SqlAlchemyUnitOfWork(factory)
    with pytest.raises(RuntimeError):
        unit.commit()
    with unit:
        unit.enqueue("Created", {"id": "1"})
        unit.commit()
    with factory() as session:
        assert session.scalar(select(OutboxMessage.event_type)) == "Created"
    with pytest.raises(ValueError):
        with unit:
            unit.enqueue("Discarded", {})
            raise ValueError("rollback")
    with factory() as session:
        assert session.scalars(select(OutboxMessage)).all()[0].event_type == "Created"
    unit.close()


def test_optimistic_locking(factory: sessionmaker[Session]) -> None:
    with factory() as seed:
        seed.add(AggregateRecord(context="match", aggregate_id="1", payload={"score": 0}))
        seed.commit()
    first, second = factory(), factory()
    try:
        one = first.scalar(select(AggregateRecord))
        two = second.scalar(select(AggregateRecord))
        assert one is not None and two is not None
        one.payload = {"score": 1}
        first.commit()
        two.payload = {"score": 2}
        with pytest.raises(StaleDataError):
            second.commit()
    finally:
        first.close()
        second.close()


def test_migration_upgrade_and_downgrade() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "migrations"
        / "versions"
        / "7a5f5c10d001_create_canonical_domain_store.py"
    )
    spec = importlib.util.spec_from_file_location("canonical_migration", path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            migration.op = Operations(MigrationContext.configure(connection))
            migration.upgrade()
            names = {
                "canonical_aggregates",
                "canonical_outbox",
                "canonical_inbox",
                "canonical_audit_log",
            }
            existing = set(
                connection.dialect.get_table_names(connection)
            )
            assert names <= existing
            migration.downgrade()
            existing = set(
                connection.dialect.get_table_names(connection)
            )
            assert names.isdisjoint(existing)
    finally:
        engine.dispose()
