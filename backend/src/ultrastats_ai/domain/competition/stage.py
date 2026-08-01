"""Entidade canônica Stage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ultrastats_ai.domain.competition.aliases import (
    CompetitionAliases,
)
from ultrastats_ai.domain.competition.season import Season
from ultrastats_ai.domain.shared import (
    AliasValue,
    DomainDate,
    Name,
    PhaseType,
    StageId,
)


@dataclass(frozen=True, slots=True, eq=False)
class Stage:
    """Representa uma fase pertencente a uma temporada."""

    id: StageId
    season: Season
    name: Name
    phase_type: PhaseType
    sequence: int | None = None
    start_date: DomainDate | None = None
    end_date: DomainDate | None = None
    aliases: CompetitionAliases = field(
        default_factory=CompetitionAliases.empty
    )
    is_active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.id, StageId):
            raise TypeError("id deve ser StageId.")

        if not isinstance(self.season, Season):
            raise TypeError("season deve ser Season.")

        if not isinstance(self.name, Name):
            raise TypeError("name deve ser Name.")

        if not isinstance(self.phase_type, PhaseType):
            raise TypeError(
                "phase_type deve ser PhaseType."
            )

        if self.sequence is not None:
            if (
                isinstance(self.sequence, bool)
                or not isinstance(self.sequence, int)
            ):
                raise TypeError(
                    "sequence deve ser int ou None."
                )

            if self.sequence < 1:
                raise ValueError(
                    "sequence deve ser maior ou igual a 1."
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

        if not isinstance(self.is_active, bool):
            raise TypeError("is_active deve ser bool.")

    @property
    def season_id(self):
        return self.season.id

    @property
    def competition_id(self):
        return self.season.competition.id

    def rename(self, name: Name) -> Stage:
        if not isinstance(name, Name):
            raise TypeError("name deve ser Name.")

        return self._copy(name=name)

    def reorder(self, sequence: int | None) -> Stage:
        return self._copy(sequence=sequence)

    def change_period(
        self,
        *,
        start_date: DomainDate | None,
        end_date: DomainDate | None,
    ) -> Stage:
        return self._copy(
            start_date=start_date,
            end_date=end_date,
        )

    def add_alias(self, alias: AliasValue) -> Stage:
        return self._copy(
            aliases=self.aliases.add(alias)
        )

    def remove_alias(self, alias: AliasValue) -> Stage:
        return self._copy(
            aliases=self.aliases.discard(alias)
        )

    def activate(self) -> Stage:
        return self._copy(is_active=True)

    def deactivate(self) -> Stage:
        return self._copy(is_active=False)

    def _copy(self, **changes: object) -> Stage:
        values = {
            "id": self.id,
            "season": self.season,
            "name": self.name,
            "phase_type": self.phase_type,
            "sequence": self.sequence,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "aliases": self.aliases,
            "is_active": self.is_active,
        }

        values.update(changes)

        return Stage(**values)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Stage):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)