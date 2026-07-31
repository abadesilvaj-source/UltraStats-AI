"""Coleção de aliases do contexto competitivo."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from ultrastats_ai.domain.competition.errors import (
    AliasNotFoundError,
    DuplicateAliasError,
)
from ultrastats_ai.domain.shared import AliasValue


@dataclass(frozen=True, slots=True)
class CompetitionAliases:
    """Coleção imutável e ordenada de aliases."""

    _values: tuple[AliasValue, ...] = ()

    def __post_init__(self) -> None:
        seen: set[AliasValue] = set()

        for alias in self._values:
            if not isinstance(alias, AliasValue):
                raise TypeError(
                    "Todos os aliases devem ser AliasValue."
                )

            if alias in seen:
                raise DuplicateAliasError(
                    f"O alias {alias!s} já existe."
                )

            seen.add(alias)

    @classmethod
    def empty(cls) -> CompetitionAliases:
        return cls()

    @classmethod
    def from_iterable(
        cls,
        values: Iterable[AliasValue],
    ) -> CompetitionAliases:
        if isinstance(values, (str, bytes)):
            raise TypeError(
                "values deve ser um iterável de AliasValue."
            )

        return cls(tuple(values))

    def add(
        self,
        alias: AliasValue,
    ) -> CompetitionAliases:
        if not isinstance(alias, AliasValue):
            raise TypeError("alias deve ser AliasValue.")

        if alias in self._values:
            raise DuplicateAliasError(
                f"O alias {alias!s} já existe."
            )

        return CompetitionAliases((*self._values, alias))

    def discard(
        self,
        alias: AliasValue,
    ) -> CompetitionAliases:
        if not isinstance(alias, AliasValue):
            raise TypeError("alias deve ser AliasValue.")

        if alias not in self._values:
            raise AliasNotFoundError(
                f"O alias {alias!s} não existe."
            )

        return CompetitionAliases(
            tuple(
                current
                for current in self._values
                if current != alias
            )
        )

    def contains(self, alias: AliasValue) -> bool:
        return (
            isinstance(alias, AliasValue)
            and alias in self._values
        )

    def as_tuple(self) -> tuple[AliasValue, ...]:
        return self._values

    def __contains__(self, alias: object) -> bool:
        return alias in self._values

    def __iter__(self) -> Iterator[AliasValue]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __bool__(self) -> bool:
        return bool(self._values)