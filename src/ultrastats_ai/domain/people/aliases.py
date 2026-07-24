"""Coleção imutável de aliases de pessoas."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from ultrastats_ai.domain.people.errors import (
    DuplicatePersonAliasError,
    PersonAliasNotFoundError,
)
from ultrastats_ai.domain.shared import AliasValue


@dataclass(frozen=True, slots=True)
class PersonAliases:
    """Representa os nomes alternativos conhecidos de uma pessoa."""

    values: tuple[AliasValue, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.values, tuple):
            raise TypeError(
                "values deve ser tuple de AliasValue."
            )

        normalized_values: set[str] = set()

        for alias in self.values:
            if not isinstance(alias, AliasValue):
                raise TypeError(
                    "values deve conter somente AliasValue."
                )

            normalized = self._normalize(alias)

            if normalized in normalized_values:
                raise DuplicatePersonAliasError(
                    f"O alias {alias.value!r} está duplicado."
                )

            normalized_values.add(normalized)

    @classmethod
    def empty(cls) -> PersonAliases:
        """Cria uma coleção vazia de aliases."""

        return cls()

    def add(self, alias: AliasValue) -> PersonAliases:
        """Adiciona um alias e retorna uma nova coleção."""

        self._validate_alias(alias)

        if alias in self:
            raise DuplicatePersonAliasError(
                f"O alias {alias.value!r} já pertence à pessoa."
            )

        return PersonAliases((*self.values, alias))

    def remove(self, alias: AliasValue) -> PersonAliases:
        """Remove um alias e retorna uma nova coleção."""

        self._validate_alias(alias)

        normalized = self._normalize(alias)

        remaining = tuple(
            current
            for current in self.values
            if self._normalize(current) != normalized
        )

        if len(remaining) == len(self.values):
            raise PersonAliasNotFoundError(
                f"O alias {alias.value!r} não pertence à pessoa."
            )

        return PersonAliases(remaining)

    def contains_text(self, value: str) -> bool:
        """Verifica se um texto corresponde a algum alias."""

        if not isinstance(value, str):
            raise TypeError(
                "value deve ser str."
            )

        normalized = self._normalize_text(value)

        return any(
            self._normalize(alias) == normalized
            for alias in self.values
        )

    def __contains__(self, alias: object) -> bool:
        if not isinstance(alias, AliasValue):
            return False

        normalized = self._normalize(alias)

        return any(
            self._normalize(current) == normalized
            for current in self.values
        )

    def __iter__(self) -> Iterator[AliasValue]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def __bool__(self) -> bool:
        return bool(self.values)

    @staticmethod
    def _validate_alias(alias: AliasValue) -> None:
        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser AliasValue."
            )

    @classmethod
    def _normalize(cls, alias: AliasValue) -> str:
        return cls._normalize_text(alias.value)

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(value.split()).casefold()