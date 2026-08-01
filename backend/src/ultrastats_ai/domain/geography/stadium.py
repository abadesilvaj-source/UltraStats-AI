"""Entidade canônica que representa um estádio."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Any

from ultrastats_ai.domain.geography.aliases import Aliases
from ultrastats_ai.domain.geography.city import City
from ultrastats_ai.domain.geography.country import Country
from ultrastats_ai.domain.geography.errors import (
    StadiumNameAliasConflictError,
)
from ultrastats_ai.domain.geography.region import Region
from ultrastats_ai.domain.shared import (
    AliasValue,
    CanonicalId,
    Coordinates,
    Name,
)


@dataclass(frozen=True, slots=True, eq=False)
class Stadium:
    """Representa um estádio pertencente a uma cidade."""

    id: CanonicalId
    city: City
    name: Name
    aliases: Aliases = field(default_factory=Aliases.empty)
    coordinates: Coordinates | None = None

    def __post_init__(self) -> None:
        """Valida os tipos e invariantes da entidade."""
        if not isinstance(self.id, CanonicalId):
            raise TypeError(
                "id deve ser uma instância de CanonicalId."
            )

        if not isinstance(self.city, City):
            raise TypeError(
                "city deve ser uma instância de City."
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
    def region(self) -> Region:
        """Retorna a região da cidade do estádio."""
        return self.city.region

    @property
    def country(self) -> Country:
        """Retorna o país da cidade do estádio."""
        return self.city.country

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
                raise StadiumNameAliasConflictError(
                    "O nome principal do estádio não pode ser "
                    "repetido como alias."
                )

    def rename(self, name: Name) -> Stadium:
        """Retorna um novo estádio com outro nome principal."""
        if not isinstance(name, Name):
            raise TypeError(
                "name deve ser uma instância de Name."
            )

        return Stadium(
            id=self.id,
            city=self.city,
            name=name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    def change_city(self, city: City) -> Stadium:
        """Retorna um novo estádio vinculado a outra cidade."""
        if not isinstance(city, City):
            raise TypeError(
                "city deve ser uma instância de City."
            )

        return Stadium(
            id=self.id,
            city=city,
            name=self.name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    def add_alias(self, alias: AliasValue) -> Stadium:
        """Retorna um novo estádio contendo o alias informado."""
        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser uma instância de AliasValue."
            )

        updated_aliases = self.aliases.add(alias)

        return Stadium(
            id=self.id,
            city=self.city,
            name=self.name,
            aliases=updated_aliases,
            coordinates=self.coordinates,
        )

    def remove_alias(self, alias: AliasValue) -> Stadium:
        """Retorna um novo estádio sem o alias informado."""
        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser uma instância de AliasValue."
            )

        updated_aliases = self.aliases.discard(alias)

        return Stadium(
            id=self.id,
            city=self.city,
            name=self.name,
            aliases=updated_aliases,
            coordinates=self.coordinates,
        )

    def update_coordinates(
        self,
        coordinates: Coordinates,
    ) -> Stadium:
        """Retorna um novo estádio com coordenadas atualizadas."""
        if not isinstance(coordinates, Coordinates):
            raise TypeError(
                "coordinates deve ser uma instância "
                "de Coordinates."
            )

        return Stadium(
            id=self.id,
            city=self.city,
            name=self.name,
            aliases=self.aliases,
            coordinates=coordinates,
        )

    def clear_coordinates(self) -> Stadium:
        """Retorna um novo estádio sem coordenadas."""
        return Stadium(
            id=self.id,
            city=self.city,
            name=self.name,
            aliases=self.aliases,
            coordinates=None,
        )

    def has_alias(self, alias: AliasValue) -> bool:
        """Informa se o estádio possui o alias informado."""
        if not isinstance(alias, AliasValue):
            return False

        return self.aliases.contains(alias)

    def belongs_to_city(self, city: City) -> bool:
        """Informa se o estádio pertence à cidade informada."""
        if not isinstance(city, City):
            return False

        return self.city == city

    def belongs_to_region(self, region: Region) -> bool:
        """Informa se o estádio pertence à região informada."""
        if not isinstance(region, Region):
            return False

        return self.region == region

    def belongs_to_country(self, country: Country) -> bool:
        """Informa se o estádio pertence ao país informado."""
        if not isinstance(country, Country):
            return False

        return self.country == country

    def __eq__(self, other: Any) -> bool:
        """Compara estádios exclusivamente pela identidade."""
        if not isinstance(other, Stadium):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        """Calcula o hash a partir da identidade canônica."""
        return hash(self.id)