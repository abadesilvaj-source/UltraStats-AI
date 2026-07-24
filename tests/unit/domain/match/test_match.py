"""Testes do Aggregate Root Match."""

import pytest

from ultrastats_ai.domain.match import (
    DuplicateMatchParticipantError,
    InvalidMatchParticipantsError,
    InvalidMatchScheduleError,
    Match,
    MatchParticipantNotFoundError,
    MatchParticipantOwnershipError,
    MatchType,
)
from ultrastats_ai.domain.shared import (
    CompetitionId,
    DomainDate,
    MatchId,
    MatchParticipantId,
    MatchStatus,
    ParticipantRole,
    RoundId,
    SeasonId,
    StageId,
    TeamId,
    UtcTimestamp,
)

from .conftest import make_match, make_participant


def valid_values() -> dict[str, object]:
    match_id = MatchId.new()
    return {
        "id": match_id,
        "competition_id": CompetitionId.new(),
        "season_id": SeasonId.new(),
        "match_type": MatchType.REGULAR,
        "status": MatchStatus.SCHEDULED,
        "participants": (
            make_participant(
                match_id=match_id,
                role=ParticipantRole.HOME,
                order=1,
            ),
            make_participant(
                match_id=match_id,
                role=ParticipantRole.AWAY,
                order=2,
            ),
        ),
        "stage_id": None,
        "round_id": None,
        "scheduled_date": DomainDate("2026-08-01"),
        "scheduled_start_at": None,
    }


def test_match_is_created_with_context_and_sides() -> None:
    values = valid_values()
    match = Match(**values)  # type: ignore[arg-type]

    assert match.home.role is ParticipantRole.HOME
    assert match.away.role is ParticipantRole.AWAY
    assert match.competition_id == values["competition_id"]


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        ("id", object(), "MatchId"),
        ("competition_id", object(), "CompetitionId"),
        ("season_id", object(), "SeasonId"),
        ("match_type", "regular", "MatchType"),
        ("status", "scheduled", "MatchStatus"),
        ("stage_id", object(), "StageId ou None"),
        ("round_id", object(), "RoundId ou None"),
        ("scheduled_date", object(), "DomainDate ou None"),
        ("scheduled_start_at", object(), "UtcTimestamp ou None"),
        ("participants", [], "participants deve ser tuple"),
    ],
)
def test_match_rejects_invalid_types(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    values = valid_values()
    values[field_name] = invalid_value

    with pytest.raises(TypeError, match=message):
        Match(**values)  # type: ignore[arg-type]


def test_match_accepts_optional_competition_hierarchy() -> None:
    values = valid_values()
    values["stage_id"] = StageId.new()
    values["round_id"] = RoundId.new()
    values["scheduled_start_at"] = UtcTimestamp(
        "2026-08-01T20:00:00Z"
    )

    match = Match(**values)  # type: ignore[arg-type]

    assert isinstance(match.stage_id, StageId)
    assert isinstance(match.round_id, RoundId)


@pytest.mark.parametrize("count", [0, 1, 3])
def test_match_requires_exactly_two_participants(count: int) -> None:
    values = valid_values()
    participants = values["participants"]
    assert isinstance(participants, tuple)
    values["participants"] = (
        participants * 2
    )[:count]

    with pytest.raises(
        InvalidMatchParticipantsError,
        match="exatamente dois",
    ):
        Match(**values)  # type: ignore[arg-type]


def test_match_rejects_invalid_participant_item() -> None:
    values = valid_values()
    participants = values["participants"]
    assert isinstance(participants, tuple)
    values["participants"] = (participants[0], object())

    with pytest.raises(TypeError, match="MatchParticipant"):
        Match(**values)  # type: ignore[arg-type]


def test_scheduled_match_requires_schedule() -> None:
    values = valid_values()
    values["scheduled_date"] = None

    with pytest.raises(InvalidMatchScheduleError):
        Match(**values)  # type: ignore[arg-type]


def test_non_scheduled_match_can_lack_schedule() -> None:
    match = make_match(status=MatchStatus.POSTPONED)

    assert match.scheduled_date is None


def test_match_rejects_participant_owned_by_another_match() -> None:
    values = valid_values()
    participants = values["participants"]
    assert isinstance(participants, tuple)
    values["participants"] = (
        participants[0],
        make_participant(
            match_id=MatchId.new(),
            role=ParticipantRole.AWAY,
            order=2,
        ),
    )

    with pytest.raises(MatchParticipantOwnershipError):
        Match(**values)  # type: ignore[arg-type]


def test_match_rejects_duplicate_participant_id() -> None:
    values = valid_values()
    match_id = values["id"]
    assert isinstance(match_id, MatchId)
    participant_id = MatchParticipantId.new()
    values["participants"] = (
        make_participant(
            id=participant_id,
            match_id=match_id,
            role=ParticipantRole.HOME,
            order=1,
        ),
        make_participant(
            id=participant_id,
            match_id=match_id,
            role=ParticipantRole.AWAY,
            order=2,
        ),
    )

    with pytest.raises(
        DuplicateMatchParticipantError,
        match="identidade",
    ):
        Match(**values)  # type: ignore[arg-type]


def test_match_rejects_duplicate_team() -> None:
    values = valid_values()
    match_id = values["id"]
    assert isinstance(match_id, MatchId)
    team_id = TeamId.new()
    values["participants"] = (
        make_participant(
            match_id=match_id,
            team_id=team_id,
            role=ParticipantRole.HOME,
            order=1,
        ),
        make_participant(
            match_id=match_id,
            team_id=team_id,
            role=ParticipantRole.AWAY,
            order=2,
        ),
    )

    with pytest.raises(
        DuplicateMatchParticipantError,
        match="dois lados",
    ):
        Match(**values)  # type: ignore[arg-type]


def test_match_rejects_duplicate_role() -> None:
    values = valid_values()
    participants = values["participants"]
    assert isinstance(participants, tuple)
    values["participants"] = (
        participants[0],
        make_participant(
            match_id=values["id"],  # type: ignore[arg-type]
            role=ParticipantRole.HOME,
            order=2,
        ),
    )

    with pytest.raises(
        DuplicateMatchParticipantError,
        match="papel",
    ):
        Match(**values)  # type: ignore[arg-type]


def test_match_rejects_duplicate_order() -> None:
    values = valid_values()
    participants = values["participants"]
    assert isinstance(participants, tuple)
    values["participants"] = (
        participants[0],
        make_participant(
            match_id=values["id"],  # type: ignore[arg-type]
            role=ParticipantRole.AWAY,
            order=1,
        ),
    )

    with pytest.raises(
        DuplicateMatchParticipantError,
        match="ordem",
    ):
        Match(**values)  # type: ignore[arg-type]


def test_match_requires_home_and_away_roles() -> None:
    values = valid_values()
    match_id = values["id"]
    assert isinstance(match_id, MatchId)
    values["participants"] = (
        make_participant(
            match_id=match_id,
            role=ParticipantRole.HOME,
            order=1,
        ),
        make_participant(
            match_id=match_id,
            role=ParticipantRole.NEUTRAL,
            order=2,
        ),
    )

    with pytest.raises(
        InvalidMatchParticipantsError,
        match="HOME e AWAY",
    ):
        Match(**values)  # type: ignore[arg-type]


def test_match_accepts_two_distinct_tbd_participants() -> None:
    values = valid_values()
    match_id = values["id"]
    assert isinstance(match_id, MatchId)
    values["participants"] = (
        make_participant(
            match_id=match_id,
            role=ParticipantRole.HOME,
            order=1,
            is_tbd=True,
            placeholder_name="Vencedor A",
        ),
        make_participant(
            match_id=match_id,
            role=ParticipantRole.AWAY,
            order=2,
            is_tbd=True,
            placeholder_name="Vencedor B",
        ),
    )

    match = Match(**values)  # type: ignore[arg-type]

    assert match.home.is_tbd
    assert match.away.is_tbd


def test_find_participant_searches_until_match() -> None:
    match = make_match()

    assert match.find_participant(match.away.id) is match.away


def test_find_participant_rejects_invalid_id() -> None:
    match = make_match()

    with pytest.raises(TypeError, match="MatchParticipantId"):
        match.find_participant("id")  # type: ignore[arg-type]


def test_find_participant_raises_when_missing() -> None:
    match = make_match()

    with pytest.raises(MatchParticipantNotFoundError):
        match.find_participant(MatchParticipantId.new())


def test_replace_participant_preserves_position() -> None:
    match = make_match()
    replacement = match.away.record_score(
        2,
        is_winner=True,
    )

    updated = match.replace_participant(replacement)

    assert updated.participants == (match.home, replacement)
    assert match.away.score is None


def test_replace_participant_rejects_invalid_type() -> None:
    match = make_match()

    with pytest.raises(TypeError, match="MatchParticipant"):
        match.replace_participant(object())  # type: ignore[arg-type]


def test_replace_participant_rejects_other_match() -> None:
    match = make_match()
    other = make_participant(
        match_id=MatchId.new(),
        role=ParticipantRole.HOME,
        order=1,
    )

    with pytest.raises(MatchParticipantOwnershipError):
        match.replace_participant(other)


def test_replace_participant_requires_existing_identity() -> None:
    match = make_match()
    unknown = make_participant(
        match_id=match.id,
        role=ParticipantRole.HOME,
        order=1,
    )

    with pytest.raises(MatchParticipantNotFoundError):
        match.replace_participant(unknown)


def test_reschedule_preserves_identity_and_sets_status() -> None:
    match = make_match(status=MatchStatus.POSTPONED)
    timestamp = UtcTimestamp("2026-08-02T20:00:00Z")

    updated = match.reschedule(
        scheduled_date=DomainDate("2026-08-02"),
        scheduled_start_at=timestamp,
    )

    assert updated.id == match.id
    assert updated.status is MatchStatus.SCHEDULED
    assert updated.scheduled_start_at == timestamp


def test_reschedule_requires_new_schedule() -> None:
    match = make_match(status=MatchStatus.POSTPONED)

    with pytest.raises(InvalidMatchScheduleError):
        match.reschedule(
            scheduled_date=None,
            scheduled_start_at=None,
        )


def test_change_status_returns_new_match() -> None:
    match = make_match()

    updated = match.change_status(MatchStatus.LIVE)

    assert updated.status is MatchStatus.LIVE
    assert match.status is MatchStatus.SCHEDULED


def test_change_status_rejects_invalid_type() -> None:
    match = make_match()

    with pytest.raises(TypeError, match="MatchStatus"):
        match.change_status("live")  # type: ignore[arg-type]


def test_match_equality_and_hash_use_identity() -> None:
    match = make_match()
    same_identity = Match(
        id=match.id,
        competition_id=match.competition_id,
        season_id=match.season_id,
        match_type=match.match_type,
        status=match.status,
        participants=match.participants,
        scheduled_date=match.scheduled_date,
    )

    assert match == same_identity
    assert hash(match) == hash(same_identity)
    assert match != object()
