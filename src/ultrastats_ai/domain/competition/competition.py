"""Entidade canônica Competition."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Any

from ultrastats_ai.domain.competition.aliases import (
    CompetitionAliases,
)
from ultrastats_ai.domain.competition.errors import (
    NameAliasConflictError,
)
from ultrastats_ai.domain.shared import (
    AliasValue,
    CompetitionCode,
    CompetitionId,
    CompetitionName,
    CompetitionType,
    CountryId,
)


@dataclass(frozen=True, slots=True, eq=False)
class Competition:
    """Representa uma competição esportiva canônica."""

    id: CompetitionId
    code: CompetitionCode
    name: CompetitionName
    competition_type: CompetitionType
    country_id: CountryId | None = None
    aliases: CompetitionAliases = field(
        default_factory=CompetitionAliases.empty
    )
    is_active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.id, CompetitionId):
            raise TypeError("id deve ser CompetitionId.")

        if not isinstance(self.code, CompetitionCode):
            raise TypeError("code deve ser CompetitionCode.")

        if not isinstance(self.name, CompetitionName):
            raise TypeError("name deve ser CompetitionName.")

        if not isinstance(
            self.competition_type,
            CompetitionType,
        ):
            raise TypeError(
                "competition_type deve ser CompetitionType."
            )

        if (
            self.country_id is not None
            and not isinstance(self.country_id, CountryId)
        ):
            raise TypeError(
                "country_id deve ser CountryId ou None."
            )

        if not isinstance(self.aliases, CompetitionAliases):
            raise TypeError(
                "aliases deve ser CompetitionAliases."
            )

        if not isinstance(self.is_active, bool):
            raise TypeError("is_active deve ser bool.")

        self._validate_alias_conflicts()

    @staticmethod
    def _normalize_identity_text(value: object) -> str:
        normalized = unicodedata.normalize(
            "NFKC",
            str(value),
        )

        return " ".join(normalized.split()).casefold()

    def _validate_alias_conflicts(self) -> None:
        normalized_name = self._normalize_identity_text(
            self.name
        )

        for alias in self.aliases:
            if (
                self._normalize_identity_text(alias)
                == normalized_name
            ):
                raise NameAliasConflictError(
                    "O nome principal da competição não pode "
                    "ser repetido como alias."
                )

    def rename(
        self,
        name: CompetitionName,
    ) -> Competition:
        if not isinstance(name, CompetitionName):
            raise TypeError("name deve ser CompetitionName.")

        return self._copy(name=name)

    def change_code(
        self,
        code: CompetitionCode,
    ) -> Competition:
        if not isinstance(code, CompetitionCode):
            raise TypeError("code deve ser CompetitionCode.")

        return self._copy(code=code)

    def change_type(
        self,
        competition_type: CompetitionType,
    ) -> Competition:
        if not isinstance(
            competition_type,
            CompetitionType,
        ):
            raise TypeError(
                "competition_type deve ser CompetitionType."
            )

        return self._copy(
            competition_type=competition_type
        )

    def assign_country(
        self,
        country_id: CountryId,
    ) -> Competition:
        if not isinstance(country_id, CountryId):
            raise TypeError(
                "country_id deve ser CountryId."
            )

        return self._copy(country_id=country_id)

    def clear_country(self) -> Competition:
        return self._copy(country_id=None)

    def add_alias(
        self,
        alias: AliasValue,
    ) -> Competition:
        return self._copy(
            aliases=self.aliases.add(alias)
        )

    def remove_alias(
        self,
        alias: AliasValue,
    ) -> Competition:
        return self._copy(
            aliases=self.aliases.discard(alias)
        )

    def activate(self) -> Competition:
        return self._copy(is_active=True)

    def deactivate(self) -> Competition:
        return self._copy(is_active=False)

    def _copy(self, **changes: object) -> Competition:
        values = {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "competition_type": self.competition_type,
            "country_id": self.country_id,
            "aliases": self.aliases,
            "is_active": self.is_active,
        }

        values.update(changes)

        return Competition(**values)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Competition):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)