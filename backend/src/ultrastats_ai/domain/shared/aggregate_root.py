"""Abstração base para raízes de agregados."""

from __future__ import annotations

from typing import Generic, TypeVar

from ultrastats_ai.domain.shared.domain_event import DomainEvent
from ultrastats_ai.domain.shared.entity import Entity

AggregateId = TypeVar("AggregateId")


class AggregateRoot(Entity[AggregateId], Generic[AggregateId]):
    """Entidade responsável por controlar um agregado.

    Todas as alterações externas ao agregado devem ocorrer por meio de sua
    raiz, protegendo as invariáveis do domínio.
    """

    def __init__(self, entity_id: AggregateId) -> None:
        super().__init__(entity_id)
        self._domain_events: list[DomainEvent] = []

    @property
    def domain_events(self) -> tuple[DomainEvent, ...]:
        """Retorna os eventos pendentes sem permitir alteração externa."""

        return tuple(self._domain_events)

    def record_event(self, event: DomainEvent) -> None:
        """Registra um evento de domínio pendente."""

        if not isinstance(event, DomainEvent):
            raise TypeError(
                "O evento registrado deve ser uma instância de DomainEvent."
            )

        self._domain_events.append(event)

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        """Retorna e remove todos os eventos pendentes."""

        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events

    def clear_domain_events(self) -> None:
        """Remove todos os eventos pendentes."""

        self._domain_events.clear()