"""Testes do histórico de alterações de agenda."""

import pytest

from ultrastats_ai.domain.match import (
    DuplicateScheduleChangeError,
    InvalidScheduleChangeError,
    Match,
    MatchScheduleChange,
    ScheduleChangeOwnershipError,
)
from ultrastats_ai.domain.shared import (
    DomainDate,
    MatchId,
    MatchScheduleChangeId,
    MatchStatus,
    UtcTimestamp,
)

from .conftest import make_match


def valid_values() -> dict[str, object]:
    return {
        "id": MatchScheduleChangeId.new(),
        "match_id": MatchId.new(),
        "changed_at": UtcTimestamp("2026-07-25T12:00:00Z"),
        "reason": " Alteração da competição ",
        "previous_date": DomainDate("2026-08-01"),
        "previous_start_at": None,
        "new_date": DomainDate("2026-08-02"),
        "new_start_at": UtcTimestamp("2026-08-02T20:00:00Z"),
    }


def test_schedule_change_is_created_and_normalizes_reason() -> None:
    change = MatchScheduleChange(  # type: ignore[arg-type]
        **valid_values()
    )

    assert change.reason == "Alteração da competição"


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        ("id", object(), "MatchScheduleChangeId"),
        ("match_id", object(), "MatchId"),
        ("changed_at", object(), "UtcTimestamp"),
        ("reason", object(), "reason deve ser str"),
        ("previous_date", object(), "previous_date"),
        ("previous_start_at", object(), "previous_start_at"),
        ("new_date", object(), "new_date"),
        ("new_start_at", object(), "new_start_at"),
    ],
)
def test_schedule_change_rejects_invalid_types(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    values = valid_values()
    values[field_name] = invalid_value

    with pytest.raises(TypeError, match=message):
        MatchScheduleChange(**values)  # type: ignore[arg-type]


def test_schedule_change_requires_reason() -> None:
    values = valid_values()
    values["reason"] = " "

    with pytest.raises(InvalidScheduleChangeError, match="motivo"):
        MatchScheduleChange(**values)  # type: ignore[arg-type]


def test_schedule_change_requires_new_schedule() -> None:
    values = valid_values()
    values["new_date"] = None
    values["new_start_at"] = None

    with pytest.raises(
        InvalidScheduleChangeError,
        match="nova agenda",
    ):
        MatchScheduleChange(**values)  # type: ignore[arg-type]


def test_schedule_change_must_change_schedule() -> None:
    values = valid_values()
    values["new_date"] = values["previous_date"]
    values["new_start_at"] = values["previous_start_at"]

    with pytest.raises(
        InvalidScheduleChangeError,
        match="diferente",
    ):
        MatchScheduleChange(**values)  # type: ignore[arg-type]


def make_change(
    *,
    match_id: MatchId,
    id: MatchScheduleChangeId | None = None,
) -> MatchScheduleChange:
    return MatchScheduleChange(
        id=id or MatchScheduleChangeId.new(),
        match_id=match_id,
        changed_at=UtcTimestamp("2026-07-25T12:00:00Z"),
        reason="Alteração",
        previous_date=DomainDate("2026-08-01"),
        new_date=DomainDate("2026-08-02"),
    )


def reconstruct_with_changes(
    match: Match,
    changes: object,
) -> Match:
    return Match(
        id=match.id,
        competition_id=match.competition_id,
        season_id=match.season_id,
        match_type=match.match_type,
        status=match.status,
        participants=match.participants,
        scheduled_date=match.scheduled_date,
        schedule_changes=changes,  # type: ignore[arg-type]
    )


def test_match_requires_schedule_changes_tuple() -> None:
    match = make_match()

    with pytest.raises(TypeError, match="schedule_changes deve ser tuple"):
        reconstruct_with_changes(match, [])


def test_match_rejects_invalid_schedule_change_item() -> None:
    match = make_match()

    with pytest.raises(TypeError, match="MatchScheduleChange"):
        reconstruct_with_changes(match, (object(),))


def test_match_rejects_schedule_change_from_other_match() -> None:
    match = make_match()

    with pytest.raises(ScheduleChangeOwnershipError):
        reconstruct_with_changes(
            match,
            (make_change(match_id=MatchId.new()),),
        )


def test_match_rejects_duplicate_schedule_change_id() -> None:
    match = make_match()
    change_id = MatchScheduleChangeId.new()
    first = make_change(match_id=match.id, id=change_id)
    second = make_change(match_id=match.id, id=change_id)

    with pytest.raises(DuplicateScheduleChangeError):
        reconstruct_with_changes(match, (first, second))


def test_multiple_schedule_changes_are_preserved_in_order() -> None:
    match = make_match(status=MatchStatus.POSTPONED)
    first = match.reschedule(
        change_id=MatchScheduleChangeId.new(),
        scheduled_date=DomainDate("2026-08-02"),
        scheduled_start_at=None,
        changed_at=UtcTimestamp("2026-07-25T12:00:00Z"),
        reason="Primeira alteração",
    )
    postponed = first.change_status(MatchStatus.POSTPONED)

    second = postponed.reschedule(
        change_id=MatchScheduleChangeId.new(),
        scheduled_date=DomainDate("2026-08-03"),
        scheduled_start_at=None,
        changed_at=UtcTimestamp("2026-07-26T12:00:00Z"),
        reason="Segunda alteração",
    )

    assert tuple(
        change.reason
        for change in second.schedule_changes
    ) == ("Primeira alteração", "Segunda alteração")
