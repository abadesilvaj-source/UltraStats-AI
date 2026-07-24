"""Testes das entidades operacionais restantes do Match."""

from dataclasses import replace

import pytest

from ultrastats_ai.domain.match import (
    AppointmentStatus,
    DecisionStatus,
    DuplicateMatchRecordError,
    EventStatus,
    InterruptionStatus,
    InvalidMatchRecordError,
    Lineup,
    LineupEntry,
    LineupRole,
    LineupStatus,
    LineupType,
    MatchDecision,
    MatchEvent,
    MatchInterruption,
    MatchOfficial,
    MatchPeriod,
    MatchRecordOwnershipError,
    MatchRevision,
    MatchSquad,
    MatchStatistic,
    PeriodStatus,
    PeriodType,
    RevisionStatus,
    SquadStatus,
    SquadType,
    StatisticScope,
    StatisticUnit,
)
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
    MatchPeriodId,
    MatchRevisionId,
    MatchSquadId,
    MatchStatisticId,
    OfficialRole,
    PersonId,
    PlayerId,
    ReviewType,
    UtcTimestamp,
)

from .conftest import make_match


def make_records(match_id: MatchId) -> tuple[object, ...]:
    match = make_match(id=match_id)
    participant = match.home
    assert participant.team_id is not None
    official = MatchOfficial(
        id=MatchOfficialId.new(),
        match_id=match_id,
        role=OfficialRole.REFEREE,
        status=AppointmentStatus.CONFIRMED,
        order=1,
        person_id=PersonId.new(),
    )
    period = MatchPeriod(
        id=MatchPeriodId.new(),
        match_id=match_id,
        period_type=PeriodType.FIRST_HALF,
        status=PeriodStatus.COMPLETED,
        order=1,
        planned_minutes=45,
        added_minutes=2,
        started_at=UtcTimestamp("2026-08-01T20:00:00Z"),
        ended_at=UtcTimestamp("2026-08-01T20:47:00Z"),
        home_score_at_end=1,
        away_score_at_end=0,
    )
    squad = MatchSquad(
        id=MatchSquadId.new(),
        match_id=match_id,
        participant_id=participant.id,
        team_id=participant.team_id,
        squad_type=SquadType.OFFICIAL,
        status=SquadStatus.CONFIRMED,
        maximum_players=23,
        listed_players=23,
        is_official=True,
    )
    lineup = Lineup(
        id=LineupId.new(),
        match_id=match_id,
        participant_id=participant.id,
        squad_id=squad.id,
        team_id=participant.team_id,
        lineup_type=LineupType.STARTING,
        status=LineupStatus.CONFIRMED,
        version=1,
        formation="4-3-3",
    )
    entry = LineupEntry(
        id=LineupEntryId.new(),
        lineup_id=lineup.id,
        match_id=match_id,
        participant_id=participant.id,
        squad_id=squad.id,
        team_id=participant.team_id,
        role=LineupRole.STARTER,
        person_id=PersonId.new(),
        player_id=PlayerId.new(),
        shirt_number=10,
        started_match=True,
    )
    event = MatchEvent(
        id=MatchEventId.new(),
        match_id=match_id,
        event_type=EventType.GOAL,
        status=EventStatus.CONFIRMED,
        order=1,
        period_id=period.id,
        participant_id=participant.id,
        team_id=participant.team_id,
        player_id=entry.player_id,
        minute=20,
        home_score_after=1,
        away_score_after=0,
        is_confirmed=True,
    )
    statistic = MatchStatistic(
        id=MatchStatisticId.new(),
        match_id=match_id,
        statistic_type="shots",
        scope=StatisticScope.PARTICIPANT,
        unit=StatisticUnit.COUNT,
        numeric_value=DecimalValue(8),
        participant_id=participant.id,
        is_official=True,
    )
    interruption = MatchInterruption(
        id=MatchInterruptionId.new(),
        match_id=match_id,
        interruption_type=InterruptionType.VAR_CHECK,
        status=InterruptionStatus.RESUMED,
        started_at=UtcTimestamp("2026-08-01T20:25:00Z"),
        period_id=period.id,
        minute=25,
        resumed_at=UtcTimestamp("2026-08-01T20:27:00Z"),
    )
    decision = MatchDecision(
        id=MatchDecisionId.new(),
        match_id=match_id,
        decision_type=DecisionType.AWARDED,
        status=DecisionStatus.FINAL,
        reason="Resultado homologado",
        awarded_home_score=3,
        awarded_away_score=0,
        decided_at=UtcTimestamp("2026-08-02T12:00:00Z"),
        is_final=True,
    )
    revision = MatchRevision(
        id=MatchRevisionId.new(),
        match_id=match_id,
        review_type=ReviewType.ADMINISTRATIVE,
        status=RevisionStatus.APPLIED,
        previous_version=1,
        new_version=2,
        changed_fields=("status", "score"),
        reason="Decisão oficial",
        decision_id=decision.id,
        applied_at=UtcTimestamp("2026-08-02T12:05:00Z"),
    )
    return (
        official,
        period,
        squad,
        lineup,
        entry,
        event,
        statistic,
        interruption,
        decision,
        revision,
    )


def test_all_operational_records_are_added_to_match() -> None:
    match = make_match()

    for record in make_records(match.id):
        match = match.add_record(record)

    assert len(match.officials) == 1
    assert len(match.periods) == 1
    assert len(match.squads) == 1
    assert len(match.lineups) == 1
    assert len(match.lineup_entries) == 1
    assert len(match.events) == 1
    assert len(match.statistics) == 1
    assert len(match.interruptions) == 1
    assert len(match.decisions) == 1
    assert len(match.revisions) == 1


def test_official_supports_tbd_and_requires_identity() -> None:
    match_id = MatchId.new()
    tbd = MatchOfficial(
        id=MatchOfficialId.new(),
        match_id=match_id,
        role=OfficialRole.REFEREE,
        status=AppointmentStatus.PROPOSED,
        order=1,
        is_tbd=True,
        placeholder_name="Árbitro a definir",
    )
    assert tbd.is_tbd

    with pytest.raises(InvalidMatchRecordError, match="placeholder"):
        replace(tbd, placeholder_name=None)
    with pytest.raises(InvalidMatchRecordError, match="pessoa ou árbitro"):
        replace(tbd, is_tbd=False)
    with pytest.raises(InvalidMatchRecordError, match="maior que zero"):
        replace(tbd, order=0)


def test_period_rejects_invalid_time_and_order() -> None:
    period = make_records(MatchId.new())[1]
    assert isinstance(period, MatchPeriod)

    with pytest.raises(InvalidMatchRecordError, match="temporal"):
        replace(
            period,
            ended_at=UtcTimestamp("2026-08-01T19:59:00Z"),
        )
    with pytest.raises(InvalidMatchRecordError, match="maior que zero"):
        replace(period, order=0)


def test_squad_rejects_player_overflow() -> None:
    squad = make_records(MatchId.new())[2]
    assert isinstance(squad, MatchSquad)

    with pytest.raises(InvalidMatchRecordError, match="excedem"):
        replace(squad, listed_players=squad.maximum_players + 1)


def test_lineup_requires_positive_version() -> None:
    lineup = make_records(MatchId.new())[3]
    assert isinstance(lineup, Lineup)

    with pytest.raises(InvalidMatchRecordError, match="version"):
        replace(lineup, version=0)


def test_lineup_entry_validates_participation_and_identity() -> None:
    entry = make_records(MatchId.new())[4]
    assert isinstance(entry, LineupEntry)

    with pytest.raises(InvalidMatchRecordError, match="banco"):
        replace(entry, was_substitute=True)
    with pytest.raises(InvalidMatchRecordError, match="pessoa ou jogador"):
        replace(
            entry,
            person_id=None,
            player_id=None,
            is_tbd=False,
        )
    placeholder = replace(
        entry,
        person_id=None,
        player_id=None,
        is_tbd=True,
    )
    assert placeholder.is_tbd


def test_event_requires_order_and_cannot_parent_itself() -> None:
    event = make_records(MatchId.new())[5]
    assert isinstance(event, MatchEvent)

    with pytest.raises(InvalidMatchRecordError, match="order"):
        replace(event, order=0)
    with pytest.raises(InvalidMatchRecordError, match="pai"):
        replace(event, parent_event_id=event.id)


def test_statistic_requires_named_type() -> None:
    statistic = make_records(MatchId.new())[6]
    assert isinstance(statistic, MatchStatistic)

    with pytest.raises(InvalidMatchRecordError, match="obrigatório"):
        replace(statistic, statistic_type=" ")


def test_interruption_rejects_resume_before_start() -> None:
    interruption = make_records(MatchId.new())[7]
    assert isinstance(interruption, MatchInterruption)

    with pytest.raises(InvalidMatchRecordError, match="Retomada"):
        replace(
            interruption,
            resumed_at=UtcTimestamp("2026-08-01T20:24:00Z"),
        )


def test_decision_requires_reason_and_consistent_final_status() -> None:
    decision = make_records(MatchId.new())[8]
    assert isinstance(decision, MatchDecision)

    with pytest.raises(InvalidMatchRecordError, match="reason"):
        replace(decision, reason=" ")
    with pytest.raises(InvalidMatchRecordError, match="provisória"):
        replace(decision, status=DecisionStatus.PROVISIONAL)


def test_revision_validates_versions_fields_links_and_application() -> None:
    revision = make_records(MatchId.new())[9]
    assert isinstance(revision, MatchRevision)

    with pytest.raises(InvalidMatchRecordError, match="Versões"):
        replace(revision, new_version=1)
    with pytest.raises(InvalidMatchRecordError, match="campo inválido"):
        replace(revision, changed_fields=("",))
    with pytest.raises(InvalidMatchRecordError, match="si mesma"):
        replace(revision, previous_revision_id=revision.id)
    with pytest.raises(InvalidMatchRecordError, match="applied_at"):
        replace(revision, applied_at=None)


def test_numeric_helpers_reject_invalid_and_negative_values() -> None:
    period = make_records(MatchId.new())[1]
    assert isinstance(period, MatchPeriod)

    with pytest.raises(TypeError, match="planned_minutes"):
        replace(period, planned_minutes=True)
    with pytest.raises(InvalidMatchRecordError, match="added_minutes"):
        replace(period, added_minutes=-1)


def test_required_and_optional_types_are_validated() -> None:
    official = make_records(MatchId.new())[0]
    assert isinstance(official, MatchOfficial)

    with pytest.raises(TypeError, match="id"):
        replace(official, id=object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="person_id"):
        replace(official, person_id=object())  # type: ignore[arg-type]


def test_match_record_collections_require_tuples_and_correct_types() -> None:
    match = make_match()

    with pytest.raises(TypeError, match="officials deve ser tuple"):
        replace(match, officials=[])  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="MatchOfficial"):
        replace(match, officials=(object(),))  # type: ignore[arg-type]


def test_match_rejects_record_from_another_match_and_duplicate() -> None:
    match = make_match()
    official = make_records(match.id)[0]
    assert isinstance(official, MatchOfficial)

    with pytest.raises(MatchRecordOwnershipError):
        match.add_record(
            replace(official, match_id=MatchId.new())
        )
    with pytest.raises(MatchRecordOwnershipError):
        replace(
            match,
            officials=(
                replace(official, match_id=MatchId.new()),
            ),
        )

    assigned = match.add_record(official)
    with pytest.raises(DuplicateMatchRecordError):
        assigned.add_record(official)


def test_add_record_rejects_unknown_type() -> None:
    with pytest.raises(TypeError, match="desconhecido"):
        make_match().add_record(object())


@pytest.mark.parametrize(
    ("home_score", "away_score", "home_winner", "away_winner"),
    [(1, 0, True, False), (0, 1, False, True)],
)
def test_record_event_synchronizes_summary_score(
    home_score: int,
    away_score: int,
    home_winner: bool,
    away_winner: bool,
) -> None:
    match = make_match()
    event = make_records(match.id)[5]
    assert isinstance(event, MatchEvent)

    updated = match.record_event(
        replace(
            event,
            home_score_after=home_score,
            away_score_after=away_score,
        )
    )

    assert updated.home.score == home_score
    assert updated.home.is_winner is home_winner
    assert updated.away.score == away_score
    assert updated.away.is_winner is away_winner


@pytest.mark.parametrize(
    ("home_score", "away_score"),
    [(None, None), (1, None)],
)
def test_record_event_without_complete_score_only_appends_event(
    home_score: int | None,
    away_score: int | None,
) -> None:
    match = make_match()
    event = make_records(match.id)[5]
    assert isinstance(event, MatchEvent)

    updated = match.record_event(
        replace(
            event,
            home_score_after=home_score,
            away_score_after=away_score,
        )
    )

    assert len(updated.events) == 1
    assert updated.home.score is None


def test_record_event_rejects_invalid_type() -> None:
    with pytest.raises(TypeError, match="event"):
        make_match().record_event(object())  # type: ignore[arg-type]
