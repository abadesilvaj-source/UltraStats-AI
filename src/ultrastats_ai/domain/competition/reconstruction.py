"""Estados de reconstrução do contexto competitivo."""

from __future__ import annotations

from dataclasses import dataclass, field

from ultrastats_ai.domain.competition.aliases import (
    CompetitionAliases,
)
from ultrastats_ai.domain.competition.competition import (
    Competition,
)
from ultrastats_ai.domain.competition.round import Round
from ultrastats_ai.domain.competition.season import Season
from ultrastats_ai.domain.competition.stage import Stage
from ultrastats_ai.domain.competition.tie import Tie
from ultrastats_ai.domain.competition.tie_match_reference import (
    TieMatchReference,
)
from ultrastats_ai.domain.shared import (
    CompetitionCode,
    CompetitionId,
    CompetitionName,
    CompetitionType,
    CountryId,
    DomainDate,
    Name,
    PhaseType,
    RoundId,
    RoundNumber,
    RoundType,
    SeasonId,
    SeasonStatus,
    StageId,
    TieId,
)


@dataclass(frozen=True, slots=True)
class CompetitionReconstruction:
    id: CompetitionId
    code: CompetitionCode
    name: CompetitionName
    competition_type: CompetitionType
    country_id: CountryId | None = None
    aliases: CompetitionAliases = field(
        default_factory=CompetitionAliases.empty
    )
    is_active: bool = True

    def restore(self) -> Competition:
        return Competition(
            id=self.id,
            code=self.code,
            name=self.name,
            competition_type=self.competition_type,
            country_id=self.country_id,
            aliases=self.aliases,
            is_active=self.is_active,
        )

    @classmethod
    def from_entity(
        cls,
        entity: Competition,
    ) -> CompetitionReconstruction:
        if not isinstance(entity, Competition):
            raise TypeError(
                "entity deve ser Competition."
            )

        return cls(
            id=entity.id,
            code=entity.code,
            name=entity.name,
            competition_type=entity.competition_type,
            country_id=entity.country_id,
            aliases=entity.aliases,
            is_active=entity.is_active,
        )


@dataclass(frozen=True, slots=True)
class SeasonReconstruction:
    id: SeasonId
    competition: Competition
    name: Name
    status: SeasonStatus
    start_date: DomainDate | None = None
    end_date: DomainDate | None = None
    aliases: CompetitionAliases = field(
        default_factory=CompetitionAliases.empty
    )
    is_current: bool = False
    is_active: bool = True

    def restore(self) -> Season:
        return Season(
            id=self.id,
            competition=self.competition,
            name=self.name,
            status=self.status,
            start_date=self.start_date,
            end_date=self.end_date,
            aliases=self.aliases,
            is_current=self.is_current,
            is_active=self.is_active,
        )

    @classmethod
    def from_entity(
        cls,
        entity: Season,
    ) -> SeasonReconstruction:
        if not isinstance(entity, Season):
            raise TypeError("entity deve ser Season.")

        return cls(
            id=entity.id,
            competition=entity.competition,
            name=entity.name,
            status=entity.status,
            start_date=entity.start_date,
            end_date=entity.end_date,
            aliases=entity.aliases,
            is_current=entity.is_current,
            is_active=entity.is_active,
        )


@dataclass(frozen=True, slots=True)
class StageReconstruction:
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

    def restore(self) -> Stage:
        return Stage(
            id=self.id,
            season=self.season,
            name=self.name,
            phase_type=self.phase_type,
            sequence=self.sequence,
            start_date=self.start_date,
            end_date=self.end_date,
            aliases=self.aliases,
            is_active=self.is_active,
        )

    @classmethod
    def from_entity(
        cls,
        entity: Stage,
    ) -> StageReconstruction:
        if not isinstance(entity, Stage):
            raise TypeError("entity deve ser Stage.")

        return cls(
            id=entity.id,
            season=entity.season,
            name=entity.name,
            phase_type=entity.phase_type,
            sequence=entity.sequence,
            start_date=entity.start_date,
            end_date=entity.end_date,
            aliases=entity.aliases,
            is_active=entity.is_active,
        )


@dataclass(frozen=True, slots=True)
class RoundReconstruction:
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

    def restore(self) -> Round:
        return Round(
            id=self.id,
            season=self.season,
            name=self.name,
            round_type=self.round_type,
            stage=self.stage,
            round_number=self.round_number,
            sequence=self.sequence,
            start_date=self.start_date,
            end_date=self.end_date,
            aliases=self.aliases,
            is_current=self.is_current,
            is_active=self.is_active,
        )

    @classmethod
    def from_entity(
        cls,
        entity: Round,
    ) -> RoundReconstruction:
        if not isinstance(entity, Round):
            raise TypeError("entity deve ser Round.")

        return cls(
            id=entity.id,
            season=entity.season,
            name=entity.name,
            round_type=entity.round_type,
            stage=entity.stage,
            round_number=entity.round_number,
            sequence=entity.sequence,
            start_date=entity.start_date,
            end_date=entity.end_date,
            aliases=entity.aliases,
            is_current=entity.is_current,
            is_active=entity.is_active,
        )


@dataclass(frozen=True, slots=True)
class TieReconstruction:
    id: TieId
    competition: Competition
    season: Season
    stage: Stage | None = None
    matches: tuple[TieMatchReference, ...] = field(
        default_factory=tuple
    )
    is_active: bool = True

    def restore(self) -> Tie:
        return Tie(
            id=self.id,
            competition=self.competition,
            season=self.season,
            stage=self.stage,
            matches=self.matches,
            is_active=self.is_active,
        )

    @classmethod
    def from_entity(
        cls,
        entity: Tie,
    ) -> TieReconstruction:
        if not isinstance(entity, Tie):
            raise TypeError("entity deve ser Tie.")

        return cls(
            id=entity.id,
            competition=entity.competition,
            season=entity.season,
            stage=entity.stage,
            matches=entity.matches,
            is_active=entity.is_active,
        )