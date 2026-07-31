"""Aggregate Root conceitual Season."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Any

from ultrastats_ai.domain.competition.aliases import (
    CompetitionAliases,
)
from ultrastats_ai.domain.competition.competition import (
    Competition,
)
from ultrastats_ai.domain.competition.errors import (
    InvalidSeasonTransitionError,
    NameAliasConflictError,
)
from ultrastats_ai.domain.shared import (
    AliasValue,
    DomainDate,
    Name,
    SeasonId,
    SeasonStatus,
)


_ALLOWED_TRANSITIONS = {
    SeasonStatus.PLANNED: frozenset(
        {
            SeasonStatus.ACTIVE,
            SeasonStatus.CANCELLED,
        }
    ),
    SeasonStatus.ACTIVE: frozenset(
        {
            SeasonStatus.SUSPENDED,
            SeasonStatus.COMPLETED,
            SeasonStatus.CANCELLED,
        }
    ),
    SeasonStatus.SUSPENDED: frozenset(
        {
            SeasonStatus.ACTIVE,
            SeasonStatus.COMPLETED,
            SeasonStatus.CANCELLED,
        }
    ),
    SeasonStatus.COMPLETED: frozenset(),
    SeasonStatus.CANCELLED: frozenset(),
}


@dataclass(frozen=True, slots=True, eq=False)
class Season:
    """Representa uma edição temporal de uma competição."""

    id: SeasonId
    competition: Competition
    name: Name
    status: SeasonStatus = SeasonStatus.PLANNED
    start_date: DomainDate | None = None
    end_date: DomainDate | None = None
    aliases: CompetitionAliases = field(
        default_factory=CompetitionAliases.empty
    )
    is_current: bool = False
    is_active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.id, SeasonId):
            raise TypeError("id deve ser SeasonId.")

        if not isinstance(self.competition, Competition):
            raise TypeError(
                "competition deve ser Competition."
            )

        if not isinstance(self.name, Name):
            raise TypeError("name deve ser Name.")

        if not isinstance(self.status, SeasonStatus):
            raise TypeError(
                "status deve ser SeasonStatus."
            )

        if (
            self.start_date is not None
            and not isinstance(self.start_date, DomainDate)
        ):
            raise TypeError(
                "start_date deve ser DomainDate ou None."
            )

        if (
            self.end_date is not None
            and not isinstance(self.end_date, DomainDate)
        ):
            raise TypeError(
                "end_date deve ser DomainDate ou None."
            )

        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date.value > self.end_date.value
        ):
            raise ValueError(
                "start_date deve ser anterior ou igual "
                "a end_date."
            )

        if not isinstance(self.aliases, CompetitionAliases):
            raise TypeError(
                "aliases deve ser CompetitionAliases."
            )

        if not isinstance(self.is_current, bool):
            raise TypeError("is_current deve ser bool.")

        if not isinstance(self.is_active, bool):
            raise TypeError("is_active deve ser bool.")

        if (
            self.is_current
            and self.status
            in {
                SeasonStatus.COMPLETED,
                SeasonStatus.CANCELLED,
            }
        ):
            raise ValueError(
                "Temporada concluída ou cancelada não "
                "pode ser atual."
            )

        self._validate_alias_conflicts()

    @staticmethod
    def _normalize(value: object) -> str:
        normalized = unicodedata.normalize(
            "NFKC",
            str(value),
        )

        return " ".join(normalized.split()).casefold()

    def _validate_alias_conflicts(self) -> None:
        normalized_name = self._normalize(self.name)

        for alias in self.aliases:
            if self._normalize(alias) == normalized_name:
                raise NameAliasConflictError(
                    "O nome da temporada não pode ser "
                    "repetido como alias."
                )

    @property
    def competition_id(self):
        return self.competition.id

    def transition_to(
        self,
        status: SeasonStatus,
    ) -> Season:
        if not isinstance(status, SeasonStatus):
            raise TypeError(
                "status deve ser SeasonStatus."
            )

        if status is self.status:
            return self

        if status not in _ALLOWED_TRANSITIONS[self.status]:
            raise InvalidSeasonTransitionError(
                f"Transição inválida de {self.status} "
                f"para {status}."
            )

        current = self.is_current

        if status in {
            SeasonStatus.COMPLETED,
            SeasonStatus.CANCELLED,
        }:
            current = False

        return self._copy(
            status=status,
            is_current=current,
        )

    def rename(self, name: Name) -> Season:
        if not isinstance(name, Name):
            raise TypeError("name deve ser Name.")

        return self._copy(name=name)

    def change_period(
        self,
        *,
        start_date: DomainDate | None,
        end_date: DomainDate | None,
    ) -> Season:
        return self._copy(
            start_date=start_date,
            end_date=end_date,
        )

    def mark_current(self) -> Season:
        return self._copy(is_current=True)

    def clear_current(self) -> Season:
        return self._copy(is_current=False)

    def add_alias(self, alias: AliasValue) -> Season:
        return self._copy(
            aliases=self.aliases.add(alias)
        )

    def remove_alias(self, alias: AliasValue) -> Season:
        return self._copy(
            aliases=self.aliases.discard(alias)
        )

    def activate(self) -> Season:
        return self._copy(is_active=True)

    def deactivate(self) -> Season:
        return self._copy(
            is_active=False,
            is_current=False,
        )

    def _copy(self, **changes: object) -> Season:
        values = {
            "id": self.id,
            "competition": self.competition,
            "name": self.name,
            "status": self.status,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "aliases": self.aliases,
            "is_current": self.is_current,
            "is_active": self.is_active,
        }

        values.update(changes)

        return Season(**values)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Season):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)