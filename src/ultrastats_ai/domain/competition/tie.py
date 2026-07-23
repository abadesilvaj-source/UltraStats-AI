"""Aggregate Root conceitual Tie."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ultrastats_ai.domain.competition.competition import (
    Competition,
)
from ultrastats_ai.domain.competition.errors import (
    CompetitionHierarchyError,
    DuplicateTieMatchError,
    DuplicateTieMatchSequenceError,
)
from ultrastats_ai.domain.competition.season import Season
from ultrastats_ai.domain.competition.stage import Stage
from ultrastats_ai.domain.competition.tie_match_reference import (
    TieMatchReference,
)
from ultrastats_ai.domain.shared import MatchId, TieId


@dataclass(frozen=True, slots=True, eq=False)
class Tie:
    """Representa um confronto com uma ou mais partidas."""

    id: TieId
    competition: Competition
    season: Season
    stage: Stage | None = None
    matches: tuple[TieMatchReference, ...] = field(
        default_factory=tuple
    )
    is_active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.id, TieId):
            raise TypeError("id deve ser TieId.")

        if not isinstance(self.competition, Competition):
            raise TypeError(
                "competition deve ser Competition."
            )

        if not isinstance(self.season, Season):
            raise TypeError("season deve ser Season.")

        if (
            self.season.competition.id
            != self.competition.id
        ):
            raise CompetitionHierarchyError(
                "A temporada do confronto deve pertencer "
                "à competição informada."
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
                "A fase do confronto deve pertencer "
                "à temporada informada."
            )

        if not isinstance(self.matches, tuple):
            raise TypeError("matches deve ser tuple.")

        if not isinstance(self.is_active, bool):
            raise TypeError("is_active deve ser bool.")

        match_ids: set[MatchId] = set()
        sequences: set[int] = set()

        for reference in self.matches:
            if not isinstance(
                reference,
                TieMatchReference,
            ):
                raise TypeError(
                    "matches deve conter somente "
                    "TieMatchReference."
                )

            if reference.match_id in match_ids:
                raise DuplicateTieMatchError(
                    "Uma partida não pode aparecer mais "
                    "de uma vez no confronto."
                )

            if reference.sequence in sequences:
                raise DuplicateTieMatchSequenceError(
                    "A sequência das partidas deve ser única."
                )

            match_ids.add(reference.match_id)
            sequences.add(reference.sequence)

    @property
    def ordered_matches(
        self,
    ) -> tuple[TieMatchReference, ...]:
        return tuple(
            sorted(
                self.matches,
                key=lambda item: item.sequence,
            )
        )

    def add_match(
        self,
        reference: TieMatchReference,
    ) -> Tie:
        if not isinstance(
            reference,
            TieMatchReference,
        ):
            raise TypeError(
                "reference deve ser TieMatchReference."
            )

        return self._copy(
            matches=(*self.matches, reference)
        )

    def remove_match(
        self,
        match_id: MatchId,
    ) -> Tie:
        if not isinstance(match_id, MatchId):
            raise TypeError("match_id deve ser MatchId.")

        updated = tuple(
            reference
            for reference in self.matches
            if reference.match_id != match_id
        )

        if len(updated) == len(self.matches):
            raise ValueError(
                "A partida não pertence ao confronto."
            )

        return self._copy(matches=updated)

    def activate(self) -> Tie:
        return self._copy(is_active=True)

    def deactivate(self) -> Tie:
        return self._copy(is_active=False)

    def _copy(self, **changes: object) -> Tie:
        values = {
            "id": self.id,
            "competition": self.competition,
            "season": self.season,
            "stage": self.stage,
            "matches": self.matches,
            "is_active": self.is_active,
        }

        values.update(changes)

        return Tie(**values)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Tie):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)