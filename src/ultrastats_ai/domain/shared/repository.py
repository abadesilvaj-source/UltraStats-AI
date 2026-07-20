"""Contrato base para repositórios do domínio."""

from __future__ import annotations

from typing import Generic, Protocol, TypeVar

from ultrastats_ai.domain.shared.entity import Entity

EntityId = TypeVar("EntityId")
EntityType = TypeVar("EntityType", bound=Entity[object])


class Repository(
    Protocol,
    Generic[EntityType, EntityId],
):
    """Contrato mínimo para persistência de entidades.

    As implementações concretas pertencem à infraestrutura.
    """

    def get_by_id(self, entity_id: EntityId) -> EntityType | None:
        """Busca uma entidade por seu identificador."""

        ...

    def add(self, entity: EntityType) -> None:
        """Adiciona uma nova entidade à unidade de persistência."""

        ...

    def remove(self, entity: EntityType) -> None:
        """Remove uma entidade da unidade de persistência."""

        ...