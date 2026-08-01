"""Entidade canônica que representa um país."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Any

from ultrastats_ai.domain.geography.aliases import Aliases
from ultrastats_ai.domain.geography.errors import (
    CountryNameAliasConflictError,
)
from ultrastats_ai.domain.shared import (
    AliasValue,
    CanonicalId,
    Coordinates,
    CountryCode,
    Name,
)


@dataclass(frozen=True, slots=True, eq=False)
class Country:
    """Representa um país canônico do domínio."""

    id: CanonicalId
    code: CountryCode
    name: Name
    aliases: Aliases = field(default_factory=Aliases.empty)
    coordinates: Coordinates | None = None

    def __post_init__(self) -> None:
        """Valida os tipos e as invariantes da entidade."""
        if not isinstance(self.id, CanonicalId):
            raise TypeError(
                "id deve ser uma instância de CanonicalId."
            )

        if not isinstance(self.code, CountryCode):
            raise TypeError(
                "code deve ser uma instância de CountryCode."
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
        """Normaliza texto utilizado em comparações de identidade."""
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
                raise CountryNameAliasConflictError(
                    "O nome principal do país não pode ser "
                    "repetido como alias."
                )

    def rename(self, name: Name) -> Country:
        """Retorna uma nova entidade com outro nome principal."""
        if not isinstance(name, Name):
            raise TypeError(
                "name deve ser uma instância de Name."
            )

        return Country(
            id=self.id,
            code=self.code,
            name=name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    def change_code(self, code: CountryCode) -> Country:
        """Retorna uma nova entidade com outro código canônico."""
        if not isinstance(code, CountryCode):
            raise TypeError(
                "code deve ser uma instância de CountryCode."
            )

        return Country(
            id=self.id,
            code=code,
            name=self.name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    def add_alias(self, alias: AliasValue) -> Country:
        """Retorna uma nova entidade contendo o alias informado."""
        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser uma instância de AliasValue."
            )

        updated_aliases = self.aliases.add(alias)

        return Country(
            id=self.id,
            code=self.code,
            name=self.name,
            aliases=updated_aliases,
            coordinates=self.coordinates,
        )

    def remove_alias(self, alias: AliasValue) -> Country:
        """Retorna uma nova entidade sem o alias informado."""
        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser uma instância de AliasValue."
            )

        updated_aliases = self.aliases.discard(alias)

        return Country(
            id=self.id,
            code=self.code,
            name=self.name,
            aliases=updated_aliases,
            coordinates=self.coordinates,
        )

    def update_coordinates(
        self,
        coordinates: Coordinates,
    ) -> Country:
        """Retorna uma nova entidade com coordenadas atualizadas."""
        if not isinstance(coordinates, Coordinates):
            raise TypeError(
                "coordinates deve ser uma instância "
                "de Coordinates."
            )

        return Country(
            id=self.id,
            code=self.code,
            name=self.name,
            aliases=self.aliases,
            coordinates=coordinates,
        )

    def clear_coordinates(self) -> Country:
        """Retorna uma nova entidade sem coordenadas."""
        return Country(
            id=self.id,
            code=self.code,
            name=self.name,
            aliases=self.aliases,
            coordinates=None,
        )

    def has_alias(self, alias: AliasValue) -> bool:
        """Informa se o país possui o alias informado."""
        if not isinstance(alias, AliasValue):
            return False

        return self.aliases.contains(alias)

    def __eq__(self, other: Any) -> bool:
        """Compara países exclusivamente por identidade canônica."""
        if not isinstance(other, Country):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        """Calcula o hash a partir da identidade canônica."""
        return hash(self.id)