"""Testes da abstração AggregateRoot."""

from dataclasses import dataclass

from ultrastats_ai.domain.shared.aggregate_root import AggregateRoot
from ultrastats_ai.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True)
class ExampleCreated(DomainEvent):
    aggregate_id: int


class ExampleAggregate(AggregateRoot[int]):
    def create(self) -> None:
        self.record_event(
            ExampleCreated(
                aggregate_id=self.id,
            )
        )


def test_aggregate_records_domain_event() -> None:
    aggregate = ExampleAggregate(10)

    aggregate.create()

    assert len(aggregate.domain_events) == 1
    assert isinstance(aggregate.domain_events[0], ExampleCreated)


def test_pull_domain_events_returns_and_clears_events() -> None:
    aggregate = ExampleAggregate(10)
    aggregate.create()

    events = aggregate.pull_domain_events()

    assert len(events) == 1
    assert aggregate.domain_events == ()


def test_clear_domain_events_removes_pending_events() -> None:
    aggregate = ExampleAggregate(10)
    aggregate.create()

    aggregate.clear_domain_events()

    assert aggregate.domain_events == ()