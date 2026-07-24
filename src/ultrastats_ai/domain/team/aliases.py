"""Coleção imutável de aliases de uma equipe."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from ultrastats_ai.domain.shared import AliasValue
from ultrastats_ai.domain.team.errors import (
    DuplicateTeamAliasError,
    TeamAliasNotFoundError,
)


@dataclass(frozen=True, slots=True)
class TeamAliases:
    """Representa os nomes alternativos conhecidos de uma equipe."""

    values: tuple[AliasValue, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.values, tuple):
            raise TypeError(
                "values deve ser tuple[AliasValue, ...]."
            )

        normalized_values: set[str] = set()

        for alias in self.values:
            if not isinstance(alias, AliasValue):
                raise TypeError(
                    "Todos os aliases devem ser AliasValue."
                )

            normalized = self._normalize(alias.value)

            if normalized in normalized_values:
                raise DuplicateTeamAliasError(
                    "A coleção contém aliases duplicados."
                )

            normalized_values.add(normalized)

    @classmethod
    def empty(cls) -> TeamAliases:
        """Cria uma coleção vazia de aliases."""

        return cls()

    @classmethod
    def from_iterable(
        cls,
        aliases: Iterable[AliasValue],
    ) -> TeamAliases:
        """Cria a coleção a partir de um iterável."""

        if isinstance(aliases, (str, bytes)):
            raise TypeError(
                "aliases deve ser um iterável de AliasValue."
            )

        try:
            values = tuple(aliases)
        except TypeError as exc:
            raise TypeError(
                "aliases deve ser um iterável de AliasValue."
            ) from exc

        return cls(values)

    def add(
        self,
        alias: AliasValue,
    ) -> TeamAliases:
        """Adiciona um alias de maneira imutável."""

        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser AliasValue."
            )

        if self.contains_text(alias.value):
            raise DuplicateTeamAliasError(
                "O alias informado já pertence à equipe."
            )

        return TeamAliases(
            self.values + (alias,)
        )

    def remove(
        self,
        alias: AliasValue,
    ) -> TeamAliases:
        """Remove um alias de maneira imutável."""

        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser AliasValue."
            )

        normalized_target = self._normalize(alias.value)

        remaining = tuple(
            current
            for current in self.values
            if self._normalize(current.value)
            != normalized_target
        )

        if len(remaining) == len(self.values):
            raise TeamAliasNotFoundError(
                "O alias informado não pertence à equipe."
            )

        return TeamAliases(remaining)

    def contains_text(
        self,
        value: str,
    ) -> bool:
        """Verifica um alias por comparação textual normalizada."""

        if not isinstance(value, str):
            raise TypeError(
                "value deve ser str."
            )

        normalized_target = self._normalize(value)

        return any(
            self._normalize(alias.value)
            == normalized_target
            for alias in self.values
        )

    def __contains__(
        self,
        alias: object,
    ) -> bool:
        if not isinstance(alias, AliasValue):
            return False

        return self.contains_text(alias.value)

    def __iter__(self) -> Iterator[AliasValue]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def __bool__(self) -> bool:
        return bool(self.values)

    def __getitem__(
        self,
        index: int,
    ) -> AliasValue:
        return self.values[index]

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.split()).casefold()