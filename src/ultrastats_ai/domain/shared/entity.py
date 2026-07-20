"""Abstração base para entidades do domínio."""

from __future__ import annotations

from typing import Generic, TypeVar

EntityId = TypeVar("EntityId")


class Entity(Generic[EntityId]):
    """Objeto de domínio definido por sua identidade.

    Duas entidades são consideradas iguais quando:

    - possuem exatamente o mesmo tipo;
    - possuem o mesmo identificador.

    Os demais atributos não participam da comparação de identidade.
    """

    def __init__(self, entity_id: EntityId) -> None:
        if entity_id is None:
            raise ValueError("O identificador da entidade não pode ser None.")

        self._id = entity_id

    @property
    def id(self) -> EntityId:
        """Retorna o identificador da entidade."""

        return self._id

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True

        if not isinstance(other, Entity):
            return False

        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id!r})"