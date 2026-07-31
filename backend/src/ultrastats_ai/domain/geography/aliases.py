"""Coleção canônica de aliases para entidades geográficas."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from ultrastats_ai.domain.geography.errors import (
    AliasNotFoundError,
    DuplicateAliasError,
)
from ultrastats_ai.domain.shared import AliasValue


@dataclass(frozen=True, slots=True)
class Aliases:
    """Coleção imutável e ordenada de aliases canônicos."""

    _values: tuple[AliasValue, ...] = ()

    def __post_init__(self) -> None:
        """Valida que não existam aliases duplicados."""
        seen: set[AliasValue] = set()

        for alias in self._values:
            if not isinstance(alias, AliasValue):
                raise TypeError(
                    "Todos os itens de Aliases devem ser instâncias "
                    "de AliasValue."
                )

            if alias in seen:
                raise DuplicateAliasError(
                    f"O alias {alias!s} já existe na coleção."
                )

            seen.add(alias)

    @classmethod
    def empty(cls) -> Aliases:
        """Cria uma coleção vazia de aliases."""
        return cls()

    @classmethod
    def from_iterable(
        cls,
        values: Iterable[AliasValue],
    ) -> Aliases:
        """Cria a coleção a partir de um iterável de AliasValue."""
        return cls(tuple(values))

    def add(self, alias: AliasValue) -> Aliases:
        """Retorna uma nova coleção contendo o alias informado."""
        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser uma instância de AliasValue."
            )

        if alias in self._values:
            raise DuplicateAliasError(
                f"O alias {alias!s} já existe na coleção."
            )

        return Aliases((*self._values, alias))

    def discard(self, alias: AliasValue) -> Aliases:
        """Remove um alias e retorna uma nova coleção."""
        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser uma instância de AliasValue."
            )

        if alias not in self._values:
            raise AliasNotFoundError(
                f"O alias {alias!s} não existe na coleção."
            )

        return Aliases(
            tuple(
                current
                for current in self._values
                if current != alias
            )
        )

    def contains(self, alias: AliasValue) -> bool:
        """Informa se o alias pertence à coleção."""
        if not isinstance(alias, AliasValue):
            return False

        return alias in self._values

    def as_tuple(self) -> tuple[AliasValue, ...]:
        """Retorna os aliases como uma tupla imutável."""
        return self._values

    def __contains__(self, alias: object) -> bool:
        """Permite utilizar o operador `in`."""
        return alias in self._values

    def __iter__(self) -> Iterator[AliasValue]:
        """Permite iterar sobre a coleção."""
        return iter(self._values)

    def __len__(self) -> int:
        """Retorna a quantidade de aliases."""
        return len(self._values)

    def __bool__(self) -> bool:
        """Informa se a coleção possui ao menos um alias."""
        return bool(self._values)