"""Entidades operacionais subordinadas ao agregado Match."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.match.enums import (
    AppointmentStatus,
    DecisionStatus,
    EventStatus,
    InterruptionStatus,
    LineupRole,
    LineupStatus,
    LineupType,
    PeriodStatus,
    PeriodType,
    RevisionStatus,
    SquadStatus,
    SquadType,
    StatisticScope,
    StatisticUnit,
)
from ultrastats_ai.domain.match.errors import MatchDomainError
from ultrastats_ai.domain.shared import (
    DecisionType,
    DecimalValue,
    EventType,
    InterruptionType,
    LineupEntryId,
    LineupId,
    MatchDecisionId,
    MatchEventId,
    MatchId,
    MatchInterruptionId,
    MatchOfficialId,
    MatchParticipantId,
    MatchPeriodId,
    MatchRevisionId,
    MatchScheduleChangeId,
    MatchSquadId,
    MatchStatisticId,
    OfficialRole,
    Percentage,
    PersonId,
    PlayerId,
    RefereeId,
    ReviewType,
    TeamId,
    UtcTimestamp,
)


class InvalidMatchRecordError(MatchDomainError):
    """Indica dados inválidos em uma entidade interna operacional."""


def _require(value: object, expected: type, field: str) -> None:
    if not isinstance(value, expected):
        raise TypeError(f"{field} deve ser {expected.__name__}.")


def _optional(value: object, expected: type, field: str) -> None:
    if value is not None:
        _require(value, expected, field)


def _nonnegative(value: int | None, field: str) -> None:
    if value is not None and (
        not isinstance(value, int) or isinstance(value, bool)
    ):
        raise TypeError(f"{field} deve ser int ou None.")
    if value is not None and value < 0:
        raise InvalidMatchRecordError(f"{field} não pode ser negativo.")


@dataclass(frozen=True, slots=True)
class MatchOfficial:
    id: MatchOfficialId
    match_id: MatchId
    role: OfficialRole
    status: AppointmentStatus
    order: int
    person_id: PersonId | None = None
    referee_id: RefereeId | None = None
    is_tbd: bool = False
    placeholder_name: str | None = None

    def __post_init__(self) -> None:
        _require(self.id, MatchOfficialId, "id")
        _require(self.match_id, MatchId, "match_id")
        _require(self.role, OfficialRole, "role")
        _require(self.status, AppointmentStatus, "status")
        _nonnegative(self.order, "order")
        _optional(self.person_id, PersonId, "person_id")
        _optional(self.referee_id, RefereeId, "referee_id")
        _require(self.is_tbd, bool, "is_tbd")
        _optional(self.placeholder_name, str, "placeholder_name")
        if self.order == 0:
            raise InvalidMatchRecordError("order deve ser maior que zero.")
        if self.is_tbd:
            if not self.placeholder_name:
                raise InvalidMatchRecordError("Oficial TBD exige placeholder.")
        elif self.person_id is None and self.referee_id is None:
            raise InvalidMatchRecordError("Oficial exige pessoa ou árbitro.")


@dataclass(frozen=True, slots=True)
class MatchPeriod:
    id: MatchPeriodId
    match_id: MatchId
    period_type: PeriodType
    status: PeriodStatus
    order: int
    planned_minutes: int
    added_minutes: int = 0
    started_at: UtcTimestamp | None = None
    ended_at: UtcTimestamp | None = None
    home_score_at_end: int | None = None
    away_score_at_end: int | None = None

    def __post_init__(self) -> None:
        _require(self.id, MatchPeriodId, "id")
        _require(self.match_id, MatchId, "match_id")
        _require(self.period_type, PeriodType, "period_type")
        _require(self.status, PeriodStatus, "status")
        for field in (
            "order",
            "planned_minutes",
            "added_minutes",
            "home_score_at_end",
            "away_score_at_end",
        ):
            _nonnegative(getattr(self, field), field)
        _optional(self.started_at, UtcTimestamp, "started_at")
        _optional(self.ended_at, UtcTimestamp, "ended_at")
        if self.order == 0:
            raise InvalidMatchRecordError("order deve ser maior que zero.")
        if (
            self.started_at is not None
            and self.ended_at is not None
            and self.ended_at.value < self.started_at.value
        ):
            raise InvalidMatchRecordError("Período temporal inválido.")


@dataclass(frozen=True, slots=True)
class MatchSquad:
    id: MatchSquadId
    match_id: MatchId
    participant_id: MatchParticipantId
    team_id: TeamId
    squad_type: SquadType
    status: SquadStatus
    maximum_players: int
    listed_players: int
    is_official: bool = False

    def __post_init__(self) -> None:
        _require(self.id, MatchSquadId, "id")
        _require(self.match_id, MatchId, "match_id")
        _require(self.participant_id, MatchParticipantId, "participant_id")
        _require(self.team_id, TeamId, "team_id")
        _require(self.squad_type, SquadType, "squad_type")
        _require(self.status, SquadStatus, "status")
        _nonnegative(self.maximum_players, "maximum_players")
        _nonnegative(self.listed_players, "listed_players")
        _require(self.is_official, bool, "is_official")
        if self.listed_players > self.maximum_players:
            raise InvalidMatchRecordError("Convocados excedem o máximo.")


@dataclass(frozen=True, slots=True)
class Lineup:
    id: LineupId
    match_id: MatchId
    participant_id: MatchParticipantId
    squad_id: MatchSquadId
    team_id: TeamId
    lineup_type: LineupType
    status: LineupStatus
    version: int
    formation: str | None = None
    is_current: bool = True

    def __post_init__(self) -> None:
        _require(self.id, LineupId, "id")
        _require(self.match_id, MatchId, "match_id")
        _require(self.participant_id, MatchParticipantId, "participant_id")
        _require(self.squad_id, MatchSquadId, "squad_id")
        _require(self.team_id, TeamId, "team_id")
        _require(self.lineup_type, LineupType, "lineup_type")
        _require(self.status, LineupStatus, "status")
        _nonnegative(self.version, "version")
        _optional(self.formation, str, "formation")
        _require(self.is_current, bool, "is_current")
        if self.version == 0:
            raise InvalidMatchRecordError("version deve ser maior que zero.")


@dataclass(frozen=True, slots=True)
class LineupEntry:
    id: LineupEntryId
    lineup_id: LineupId
    match_id: MatchId
    participant_id: MatchParticipantId
    squad_id: MatchSquadId
    team_id: TeamId
    role: LineupRole
    person_id: PersonId | None = None
    player_id: PlayerId | None = None
    shirt_number: int | None = None
    started_match: bool = False
    was_substitute: bool = False
    remained_unused: bool = False
    is_tbd: bool = False

    def __post_init__(self) -> None:
        _require(self.id, LineupEntryId, "id")
        _require(self.lineup_id, LineupId, "lineup_id")
        _require(self.match_id, MatchId, "match_id")
        _require(self.participant_id, MatchParticipantId, "participant_id")
        _require(self.squad_id, MatchSquadId, "squad_id")
        _require(self.team_id, TeamId, "team_id")
        _require(self.role, LineupRole, "role")
        _optional(self.person_id, PersonId, "person_id")
        _optional(self.player_id, PlayerId, "player_id")
        _nonnegative(self.shirt_number, "shirt_number")
        for field in (
            "started_match",
            "was_substitute",
            "remained_unused",
            "is_tbd",
        ):
            _require(getattr(self, field), bool, field)
        if self.started_match and self.was_substitute:
            raise InvalidMatchRecordError("Titular não pode iniciar no banco.")
        if not self.is_tbd and self.person_id is None and self.player_id is None:
            raise InvalidMatchRecordError("Entrada exige pessoa ou jogador.")


@dataclass(frozen=True, slots=True)
class MatchEvent:
    id: MatchEventId
    match_id: MatchId
    event_type: EventType
    status: EventStatus
    order: int
    period_id: MatchPeriodId | None = None
    participant_id: MatchParticipantId | None = None
    team_id: TeamId | None = None
    player_id: PlayerId | None = None
    minute: int | None = None
    added_time: int = 0
    home_score_after: int | None = None
    away_score_after: int | None = None
    parent_event_id: MatchEventId | None = None
    is_confirmed: bool = False

    def __post_init__(self) -> None:
        _require(self.id, MatchEventId, "id")
        _require(self.match_id, MatchId, "match_id")
        _require(self.event_type, EventType, "event_type")
        _require(self.status, EventStatus, "status")
        for field in (
            "order",
            "minute",
            "added_time",
            "home_score_after",
            "away_score_after",
        ):
            _nonnegative(getattr(self, field), field)
        for field, expected in (
            ("period_id", MatchPeriodId),
            ("participant_id", MatchParticipantId),
            ("team_id", TeamId),
            ("player_id", PlayerId),
            ("parent_event_id", MatchEventId),
        ):
            _optional(getattr(self, field), expected, field)
        _require(self.is_confirmed, bool, "is_confirmed")
        if self.order == 0:
            raise InvalidMatchRecordError("order deve ser maior que zero.")
        if self.parent_event_id == self.id:
            raise InvalidMatchRecordError("Evento não pode ser pai de si mesmo.")


@dataclass(frozen=True, slots=True)
class MatchStatistic:
    id: MatchStatisticId
    match_id: MatchId
    statistic_type: str
    scope: StatisticScope
    unit: StatisticUnit
    numeric_value: DecimalValue
    participant_id: MatchParticipantId | None = None
    player_id: PlayerId | None = None
    percentage: Percentage | None = None
    is_official: bool = False

    def __post_init__(self) -> None:
        _require(self.id, MatchStatisticId, "id")
        _require(self.match_id, MatchId, "match_id")
        _require(self.statistic_type, str, "statistic_type")
        _require(self.scope, StatisticScope, "scope")
        _require(self.unit, StatisticUnit, "unit")
        _require(self.numeric_value, DecimalValue, "numeric_value")
        _optional(self.participant_id, MatchParticipantId, "participant_id")
        _optional(self.player_id, PlayerId, "player_id")
        _optional(self.percentage, Percentage, "percentage")
        _require(self.is_official, bool, "is_official")
        if not self.statistic_type.strip():
            raise InvalidMatchRecordError("statistic_type é obrigatório.")


@dataclass(frozen=True, slots=True)
class MatchInterruption:
    id: MatchInterruptionId
    match_id: MatchId
    interruption_type: InterruptionType
    status: InterruptionStatus
    started_at: UtcTimestamp
    period_id: MatchPeriodId | None = None
    minute: int | None = None
    resumed_at: UtcTimestamp | None = None

    def __post_init__(self) -> None:
        _require(self.id, MatchInterruptionId, "id")
        _require(self.match_id, MatchId, "match_id")
        _require(self.interruption_type, InterruptionType, "interruption_type")
        _require(self.status, InterruptionStatus, "status")
        _require(self.started_at, UtcTimestamp, "started_at")
        _optional(self.period_id, MatchPeriodId, "period_id")
        _nonnegative(self.minute, "minute")
        _optional(self.resumed_at, UtcTimestamp, "resumed_at")
        if (
            self.resumed_at is not None
            and self.resumed_at.value < self.started_at.value
        ):
            raise InvalidMatchRecordError("Retomada anterior à interrupção.")


@dataclass(frozen=True, slots=True)
class MatchDecision:
    id: MatchDecisionId
    match_id: MatchId
    decision_type: DecisionType
    status: DecisionStatus
    reason: str
    awarded_home_score: int | None = None
    awarded_away_score: int | None = None
    decided_at: UtcTimestamp | None = None
    is_final: bool = False

    def __post_init__(self) -> None:
        _require(self.id, MatchDecisionId, "id")
        _require(self.match_id, MatchId, "match_id")
        _require(self.decision_type, DecisionType, "decision_type")
        _require(self.status, DecisionStatus, "status")
        _require(self.reason, str, "reason")
        _nonnegative(self.awarded_home_score, "awarded_home_score")
        _nonnegative(self.awarded_away_score, "awarded_away_score")
        _optional(self.decided_at, UtcTimestamp, "decided_at")
        _require(self.is_final, bool, "is_final")
        if not self.reason.strip():
            raise InvalidMatchRecordError("reason é obrigatório.")
        if self.is_final and self.status is DecisionStatus.PROVISIONAL:
            raise InvalidMatchRecordError("Decisão final não pode ser provisória.")


@dataclass(frozen=True, slots=True)
class MatchRevision:
    id: MatchRevisionId
    match_id: MatchId
    review_type: ReviewType
    status: RevisionStatus
    previous_version: int
    new_version: int
    changed_fields: tuple[str, ...]
    reason: str
    previous_revision_id: MatchRevisionId | None = None
    decision_id: MatchDecisionId | None = None
    schedule_change_id: MatchScheduleChangeId | None = None
    applied_at: UtcTimestamp | None = None

    def __post_init__(self) -> None:
        _require(self.id, MatchRevisionId, "id")
        _require(self.match_id, MatchId, "match_id")
        _require(self.review_type, ReviewType, "review_type")
        _require(self.status, RevisionStatus, "status")
        _nonnegative(self.previous_version, "previous_version")
        _nonnegative(self.new_version, "new_version")
        _require(self.changed_fields, tuple, "changed_fields")
        _require(self.reason, str, "reason")
        _optional(
            self.previous_revision_id,
            MatchRevisionId,
            "previous_revision_id",
        )
        _optional(self.decision_id, MatchDecisionId, "decision_id")
        _optional(
            self.schedule_change_id,
            MatchScheduleChangeId,
            "schedule_change_id",
        )
        _optional(self.applied_at, UtcTimestamp, "applied_at")
        if (
            self.previous_version == 0
            or self.new_version <= self.previous_version
        ):
            raise InvalidMatchRecordError("Versões da revisão são inválidas.")
        if any(
            not isinstance(field, str) or not field
            for field in self.changed_fields
        ):
            raise InvalidMatchRecordError("changed_fields contém campo inválido.")
        if self.previous_revision_id == self.id:
            raise InvalidMatchRecordError("Revisão não pode referenciar a si mesma.")
        if self.status is RevisionStatus.APPLIED and self.applied_at is None:
            raise InvalidMatchRecordError("Revisão aplicada exige applied_at.")
