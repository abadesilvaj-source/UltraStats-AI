"""Entidade canônica Round."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ultrastats_ai.domain.competition.aliases import (
    CompetitionAliases,
)
from ultrastats_ai.domain.competition.errors import (
    CompetitionHierarchyError,
)
from ultrastats_ai.domain.competition.season import Season
from ultrastats_ai.domain.competition.stage import Stage
from ultrastats_ai.domain.shared import (
    AliasValue,
    DomainDate,
    Name,
    RoundId,
    RoundNumber,
    RoundType,
)


@dataclass(frozen=True, slots=True, eq=False)
class Round:
    """Representa uma rodada de uma temporada."""

    id: RoundId
    season: Season
    name: Name
    round_type: RoundType
    stage: Stage | None = None
    round_number: RoundNumber | None = None
    sequence: int | None = None
    start_date: DomainDate | None = None
    end_date: DomainDate | None = None
    aliases: CompetitionAliases = field(
        default_factory=CompetitionAliases.empty
    )
    is_current: bool = False
    is_active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.id, RoundId):
            raise TypeError("id deve ser RoundId.")

        if not isinstance(self.season, Season):
            raise TypeError("season deve ser Season.")

        if not isinstance(self.name, Name):
            raise TypeError("name deve ser Name.")

        if not isinstance(self.round_type, RoundType):
            raise TypeError(
                "round_type deve ser RoundType."
            )

        if (
            self.stage is not None
            and not isinstance(self.stage, Stage)
        ):
            raise TypeError(
                "stage deve ser Stage ou None."
            )

        if (
            self.stage is not None
            and self.stage.season.id != self.season.id
        ):
            raise CompetitionHierarchyError(
                "A fase da rodada deve pertencer "
                "à mesma temporada."
            )

        if (
            self.round_number is not None
            and not isinstance(
                self.round_number,
                RoundNumber,
            )
        ):
            raise TypeError(
                "round_number deve ser RoundNumber ou None."
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

        if not isinstance(self.is_current, bool):
            raise TypeError("is_current deve ser bool.")

        if not isinstance(self.is_active, bool):
            raise TypeError("is_active deve ser bool.")

    @property
    def competition_id(self):
        return self.season.competition.id

    @property
    def season_id(self):
        return self.season.id

    @property
    def stage_id(self):
        if self.stage is None:
            return None

        return self.stage.id

    def assign_stage(self, stage: Stage) -> Round:
        if not isinstance(stage, Stage):
            raise TypeError("stage deve ser Stage.")

        return self._copy(stage=stage)

    def clear_stage(self) -> Round:
        return self._copy(stage=None)

    def reorder(self, sequence: int | None) -> Round:
        return self._copy(sequence=sequence)

    def renumber(
        self,
        round_number: RoundNumber | None,
    ) -> Round:
        return self._copy(round_number=round_number)

    def mark_current(self) -> Round:
        return self._copy(is_current=True)

    def clear_current(self) -> Round:
        return self._copy(is_current=False)

    def deactivate(self) -> Round:
        return self._copy(
            is_active=False,
            is_current=False,
        )

    def activate(self) -> Round:
        return self._copy(is_active=True)

    def add_alias(self, alias: AliasValue) -> Round:
        return self._copy(
            aliases=self.aliases.add(alias)
        )

    def remove_alias(self, alias: AliasValue) -> Round:
        return self._copy(
            aliases=self.aliases.discard(alias)
        )

    def _copy(self, **changes: object) -> Round:
        values = {
            "id": self.id,
            "season": self.season,
            "name": self.name,
            "round_type": self.round_type,
            "stage": self.stage,
            "round_number": self.round_number,
            "sequence": self.sequence,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "aliases": self.aliases,
            "is_current": self.is_current,
            "is_active": self.is_active,
        }

        values.update(changes)

        return Round(**values)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Round):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)