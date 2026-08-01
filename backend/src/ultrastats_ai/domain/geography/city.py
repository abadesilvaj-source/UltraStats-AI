"""Entidade canônica que representa uma cidade."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Any

from ultrastats_ai.domain.geography.aliases import Aliases
from ultrastats_ai.domain.geography.country import Country
from ultrastats_ai.domain.geography.errors import (
    CityNameAliasConflictError,
)
from ultrastats_ai.domain.geography.region import Region
from ultrastats_ai.domain.shared import (
    AliasValue,
    CanonicalId,
    Coordinates,
    Name,
)


@dataclass(frozen=True, slots=True, eq=False)
class City:
    """Representa uma cidade pertencente a uma região."""

    id: CanonicalId
    region: Region
    name: Name
    aliases: Aliases = field(default_factory=Aliases.empty)
    coordinates: Coordinates | None = None

    def __post_init__(self) -> None:
        """Valida os tipos e invariantes da entidade."""
        if not isinstance(self.id, CanonicalId):
            raise TypeError(
                "id deve ser uma instância de CanonicalId."
            )

        if not isinstance(self.region, Region):
            raise TypeError(
                "region deve ser uma instância de Region."
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

    @property
    def country(self) -> Country:
        """Retorna o país da região à qual a cidade pertence."""
        return self.region.country

    @staticmethod
    def _normalize_identity_text(value: object) -> str:
        """Normaliza textos usados em comparações de identidade."""
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
        """Impede a repetição do nome principal como alias."""
        normalized_name = cls._normalize_identity_text(name)

        for alias in aliases:
            normalized_alias = cls._normalize_identity_text(alias)

            if normalized_alias == normalized_name:
                raise CityNameAliasConflictError(
                    "O nome principal da cidade não pode ser "
                    "repetido como alias."
                )

    def rename(self, name: Name) -> City:
        """Retorna uma nova cidade com outro nome principal."""
        if not isinstance(name, Name):
            raise TypeError(
                "name deve ser uma instância de Name."
            )

        return City(
            id=self.id,
            region=self.region,
            name=name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    def change_region(self, region: Region) -> City:
        """Retorna uma nova cidade vinculada a outra região."""
        if not isinstance(region, Region):
            raise TypeError(
                "region deve ser uma instância de Region."
            )

        return City(
            id=self.id,
            region=region,
            name=self.name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    def add_alias(self, alias: AliasValue) -> City:
        """Retorna uma nova cidade contendo o alias informado."""
        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser uma instância de AliasValue."
            )

        updated_aliases = self.aliases.add(alias)

        return City(
            id=self.id,
            region=self.region,
            name=self.name,
            aliases=updated_aliases,
            coordinates=self.coordinates,
        )

    def remove_alias(self, alias: AliasValue) -> City:
        """Retorna uma nova cidade sem o alias informado."""
        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser uma instância de AliasValue."
            )

        updated_aliases = self.aliases.discard(alias)

        return City(
            id=self.id,
            region=self.region,
            name=self.name,
            aliases=updated_aliases,
            coordinates=self.coordinates,
        )

    def update_coordinates(
        self,
        coordinates: Coordinates,
    ) -> City:
        """Retorna uma nova cidade com coordenadas atualizadas."""
        if not isinstance(coordinates, Coordinates):
            raise TypeError(
                "coordinates deve ser uma instância "
                "de Coordinates."
            )

        return City(
            id=self.id,
            region=self.region,
            name=self.name,
            aliases=self.aliases,
            coordinates=coordinates,
        )

    def clear_coordinates(self) -> City:
        """Retorna uma nova cidade sem coordenadas."""
        return City(
            id=self.id,
            region=self.region,
            name=self.name,
            aliases=self.aliases,
            coordinates=None,
        )

    def has_alias(self, alias: AliasValue) -> bool:
        """Informa se a cidade possui o alias informado."""
        if not isinstance(alias, AliasValue):
            return False

        return self.aliases.contains(alias)

    def belongs_to_region(self, region: Region) -> bool:
        """Informa se a cidade pertence à região informada."""
        if not isinstance(region, Region):
            return False

        return self.region == region

    def belongs_to_country(self, country: Country) -> bool:
        """Informa se a cidade pertence ao país informado."""
        if not isinstance(country, Country):
            return False

        return self.country == country

    def __eq__(self, other: Any) -> bool:
        """Compara cidades exclusivamente pela identidade."""
        if not isinstance(other, City):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        """Calcula o hash a partir da identidade canônica."""
        return hash(self.id)