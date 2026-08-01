"""Contratos de persistência do contexto competitivo."""

from __future__ import annotations

from typing import Protocol

from ultrastats_ai.domain.competition.competition import (
    Competition,
)
from ultrastats_ai.domain.competition.history import (
    CompetitionHistoryEntry,
)
from ultrastats_ai.domain.competition.season import Season
from ultrastats_ai.domain.competition.tie import Tie
from ultrastats_ai.domain.shared import (
    CanonicalId,
    CompetitionId,
    SeasonId,
    TieId,
)


class CompetitionRepository(Protocol):
    def get_by_id(
        self,
        competition_id: CompetitionId,
    ) -> Competition | None:
        ...

    def save(self, competition: Competition) -> None:
        ...

    def delete(
        self,
        competition_id: CompetitionId,
    ) -> None:
        ...

    def list_all(self) -> tuple[Competition, ...]:
        ...


class SeasonRepository(Protocol):
    def get_by_id(
        self,
        season_id: SeasonId,
    ) -> Season | None:
        ...

    def list_by_competition(
        self,
        competition_id: CompetitionId,
    ) -> tuple[Season, ...]:
        ...

    def save(self, season: Season) -> None:
        ...

    def delete(self, season_id: SeasonId) -> None:
        ...


class TieRepository(Protocol):
    def get_by_id(
        self,
        tie_id: TieId,
    ) -> Tie | None:
        ...

    def list_by_season(
        self,
        season_id: SeasonId,
    ) -> tuple[Tie, ...]:
        ...

    def save(self, tie: Tie) -> None:
        ...

    def delete(self, tie_id: TieId) -> None:
        ...


class CompetitionHistoryRepository(Protocol):
    def append(
        self,
        entry: CompetitionHistoryEntry,
    ) -> None:
        ...

    def get_by_id(
        self,
        history_id: CanonicalId,
    ) -> CompetitionHistoryEntry | None:
        ...

    def list_for_entity(
        self,
        entity_id: CanonicalId,
    ) -> tuple[CompetitionHistoryEntry, ...]:
        ...