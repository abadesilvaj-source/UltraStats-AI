"""Entidade canônica que representa uma região geográfica."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Any

from ultrastats_ai.domain.geography.aliases import Aliases
from ultrastats_ai.domain.geography.country import Country
from ultrastats_ai.domain.geography.errors import (
    RegionNameAliasConflictError,
)
from ultrastats_ai.domain.shared import (
    AliasValue,
    CanonicalId,
    Coordinates,
    Name,
)


@dataclass(frozen=True, slots=True, eq=False)
class Region:
    """Representa uma região pertencente a um país."""

    id: CanonicalId
    country: Country
    name: Name
    aliases: Aliases = field(default_factory=Aliases.empty)
    coordinates: Coordinates | None = None

    def __post_init__(self) -> None:
        """Valida tipos e invariantes da entidade."""
        if not isinstance(self.id, CanonicalId):
            raise TypeError(
                "id deve ser uma instância de CanonicalId."
            )

        if not isinstance(self.country, Country):
            raise TypeError(
                "country deve ser uma instância de Country."
            )

        if not isinstance(self.name, Name):
            raise TypeError(
                "name deve ser uma instância de Name."
            )

        if not isinstance(self.aliases, Aliases):
            raise TypeError(
                "aliases deve ser uma instância de Aliases."
            )

        if (
            self.coordinates is not None
            and not isinstance(self.coordinates, Coordinates)
        ):
            raise TypeError(
                "coordinates deve ser uma instância de "
                "Coordinates ou None."
            )

        self._validate_name_alias_conflicts(
            name=self.name,
            aliases=self.aliases,
        )

    @staticmethod
    def _normalize_identity_text(value: object) -> str:
        """Normaliza texto utilizado nas comparações de identidade."""
        normalized = unicodedata.normalize(
            "NFKC",
            str(value),
        )

        collapsed = " ".join(normalized.split())

        return collapsed.casefold()

    @classmethod
    def _validate_name_alias_conflicts(
        cls,
        *,
        name: Name,
        aliases: Aliases,
    ) -> None:
        """Impede que o nome principal seja repetido como alias."""
        normalized_name = cls._normalize_identity_text(name)

        for alias in aliases:
            normalized_alias = cls._normalize_identity_text(alias)

            if normalized_alias == normalized_name:
                raise RegionNameAliasConflictError(
                    "O nome principal da região não pode ser "
                    "repetido como alias."
                )

    def rename(self, name: Name) -> Region:
        """Retorna uma nova região com outro nome principal."""
        if not isinstance(name, Name):
            raise TypeError(
                "name deve ser uma instância de Name."
            )

        return Region(
            id=self.id,
            country=self.country,
            name=name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    def change_country(self, country: Country) -> Region:
        """Retorna uma nova região vinculada a outro país."""
        if not isinstance(country, Country):
            raise TypeError(
                "country deve ser uma instância de Country."
            )

        return Region(
            id=self.id,
            country=country,
            name=self.name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    def add_alias(self, alias: AliasValue) -> Region:
        """Retorna uma nova região contendo o alias informado."""
        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser uma instância de AliasValue."
            )

        updated_aliases = self.aliases.add(alias)

        return Region(
            id=self.id,
            country=self.country,
            name=self.name,
            aliases=updated_aliases,
            coordinates=self.coordinates,
        )

    def remove_alias(self, alias: AliasValue) -> Region:
        """Retorna uma nova região sem o alias informado."""
        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser uma instância de AliasValue."
            )

        updated_aliases = self.aliases.discard(alias)

        return Region(
            id=self.id,
            country=self.country,
            name=self.name,
            aliases=updated_aliases,
            coordinates=self.coordinates,
        )

    def update_coordinates(
        self,
        coordinates: Coordinates,
    ) -> Region:
        """Retorna uma nova região com coordenadas atualizadas."""
        if not isinstance(coordinates, Coordinates):
            raise TypeError(
                "coordinates deve ser uma instância "
                "de Coordinates."
            )

        return Region(
            id=self.id,
            country=self.country,
            name=self.name,
            aliases=self.aliases,
            coordinates=coordinates,
        )

    def clear_coordinates(self) -> Region:
        """Retorna uma nova região sem coordenadas."""
        return Region(
            id=self.id,
            country=self.country,
            name=self.name,
            aliases=self.aliases,
            coordinates=None,
        )

    def has_alias(self, alias: AliasValue) -> bool:
        """Informa se a região possui o alias informado."""
        if not isinstance(alias, AliasValue):
            return False

        return self.aliases.contains(alias)

    def belongs_to(self, country: Country) -> bool:
        """Informa se a região pertence ao país informado."""
        if not isinstance(country, Country):
            return False

        return self.country == country

    def __eq__(self, other: Any) -> bool:
        """Compara regiões exclusivamente pela identidade."""
        if not isinstance(other, Region):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        """Calcula o hash a partir da identidade canônica."""
        return hash(self.id)