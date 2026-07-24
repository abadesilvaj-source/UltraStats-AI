"""Testes dos registros históricos do People Context."""

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone, tzinfo

import pytest

from ultrastats_ai.domain.people import (
    PeopleHistoryAction,
    PeopleProfileType,
    PersonHistoryEntry,
)
from ultrastats_ai.domain.shared import PersonId

class InvalidTimezone(tzinfo):
    """Timezone propositalmente inválido para testar validação."""

    def utcoffset(self, dt: datetime | None) -> None:
        return None

    def dst(self, dt: datetime | None) -> None:
        return None

    def tzname(self, dt: datetime | None) -> str:
        return "INVALID"

def utc_datetime() -> datetime:
    return datetime(
        2026,
        7,
        23,
        12,
        30,
        tzinfo=timezone.utc,
    )


def make_entry(
    *,
    person_id: PersonId | object | None = None,
    action: PeopleHistoryAction | object = (
        PeopleHistoryAction.PERSON_CREATED
    ),
    occurred_at: datetime | object | None = None,
    profile_type: PeopleProfileType | object | None = None,
    previous_value: str | object | None = None,
    current_value: str | object | None = None,
    metadata: object = None,
) -> PersonHistoryEntry:
    return PersonHistoryEntry.create(
        person_id=(
            PersonId.new()
            if person_id is None
            else person_id
        ),
        action=action,
        occurred_at=(
            utc_datetime()
            if occurred_at is None
            else occurred_at
        ),
        profile_type=profile_type,
        previous_value=previous_value,
        current_value=current_value,
        metadata=metadata,
    )


def test_history_entry_is_created() -> None:
    person_id = PersonId.new()
    occurred_at = utc_datetime()

    entry = make_entry(
        person_id=person_id,
        occurred_at=occurred_at,
    )

    assert entry.person_id == person_id
    assert (
        entry.action
        is PeopleHistoryAction.PERSON_CREATED
    )
    assert entry.occurred_at == occurred_at
    assert entry.profile_type is None
    assert dict(entry.metadata or {}) == {}


def test_history_entry_normalizes_datetime_to_utc() -> None:
    local_timezone = timezone(timedelta(hours=-3))

    local_datetime = datetime(
        2026,
        7,
        23,
        9,
        30,
        tzinfo=local_timezone,
    )

    entry = make_entry(
        occurred_at=local_datetime,
    )

    assert entry.occurred_at == utc_datetime()
    assert entry.occurred_at.tzinfo is timezone.utc


def test_history_entry_accepts_profile_type() -> None:
    entry = make_entry(
        action=(
            PeopleHistoryAction.PLAYER_PROFILE_ADDED
        ),
        profile_type=PeopleProfileType.PLAYER,
    )

    assert (
        entry.profile_type
        is PeopleProfileType.PLAYER
    )


def test_history_entry_preserves_values() -> None:
    entry = make_entry(
        action=PeopleHistoryAction.PERSON_RENAMED,
        previous_value="Nome antigo",
        current_value="Nome novo",
    )

    assert entry.previous_value == "Nome antigo"
    assert entry.current_value == "Nome novo"


def test_history_entry_normalizes_metadata() -> None:
    entry = make_entry(
        metadata={
            " source ": " api ",
            " provider ": " opta ",
        },
    )

    assert dict(entry.metadata or {}) == {
        "source": "api",
        "provider": "opta",
    }


def test_history_metadata_is_immutable() -> None:
    entry = make_entry(
        metadata={"source": "api"},
    )

    with pytest.raises(TypeError):
        entry.metadata["source"] = "manual"  # type: ignore[index]


def test_history_entry_rejects_invalid_person_id() -> None:
    with pytest.raises(
        TypeError,
        match="person_id deve ser PersonId",
    ):
        make_entry(person_id="invalid")


def test_history_entry_rejects_invalid_action() -> None:
    with pytest.raises(
        TypeError,
        match="action deve ser PeopleHistoryAction",
    ):
        make_entry(action="person_created")


def test_history_entry_rejects_invalid_datetime() -> None:
    with pytest.raises(
        TypeError,
        match="occurred_at deve ser datetime",
    ):
        make_entry(occurred_at="2026-07-23")


def test_history_entry_rejects_naive_datetime() -> None:
    with pytest.raises(
        ValueError,
        match="occurred_at deve possuir timezone",
    ):
        make_entry(
            occurred_at=datetime(2026, 7, 23, 12, 30)
        )

def test_history_entry_rejects_timezone_with_invalid_offset() -> None:
    invalid_datetime = datetime(
        2026,
        7,
        23,
        12,
        30,
        tzinfo=InvalidTimezone(),
    )

    with pytest.raises(
        ValueError,
        match="occurred_at deve possuir timezone válido",
    ):
        make_entry(
            occurred_at=invalid_datetime
        )

def test_history_entry_rejects_invalid_profile_type() -> None:
    with pytest.raises(
        TypeError,
        match="profile_type deve ser PeopleProfileType",
    ):
        make_entry(profile_type="player")


@pytest.mark.parametrize(
    "field_name",
    [
        "previous_value",
        "current_value",
    ],
)
def test_history_entry_rejects_invalid_value_type(
    field_name: str,
) -> None:
    arguments = {
        field_name: 123,
    }

    with pytest.raises(TypeError):
        make_entry(**arguments)


@pytest.mark.parametrize(
    "field_name",
    [
        "previous_value",
        "current_value",
    ],
)
def test_history_entry_rejects_empty_value(
    field_name: str,
) -> None:
    arguments = {
        field_name: "   ",
    }

    with pytest.raises(ValueError):
        make_entry(**arguments)


def test_history_entry_rejects_invalid_metadata_type() -> None:
    with pytest.raises(
        TypeError,
        match="metadata deve ser Mapping",
    ):
        make_entry(metadata=["source", "api"])


def test_history_entry_rejects_non_string_metadata_key() -> None:
    with pytest.raises(
        TypeError,
        match="chaves de metadata devem ser str",
    ):
        make_entry(metadata={1: "api"})


def test_history_entry_rejects_non_string_metadata_value() -> None:
    with pytest.raises(
        TypeError,
        match="valores de metadata devem ser str",
    ):
        make_entry(metadata={"source": 123})


def test_history_entry_rejects_empty_metadata_key() -> None:
    with pytest.raises(
        ValueError,
        match="chaves de metadata não podem",
    ):
        make_entry(metadata={"   ": "api"})


def test_history_entry_rejects_empty_metadata_value() -> None:
    with pytest.raises(
        ValueError,
        match="valores de metadata não podem",
    ):
        make_entry(metadata={"source": "   "})


def test_history_entry_reconstructs_persisted_state() -> None:
    person_id = PersonId.new()
    occurred_at = utc_datetime()

    entry = PersonHistoryEntry.reconstruct(
        person_id=person_id,
        action=PeopleHistoryAction.ALIAS_ADDED,
        occurred_at=occurred_at,
        current_value="Nome alternativo",
        metadata={"source": "database"},
    )

    assert entry.person_id == person_id
    assert entry.action is PeopleHistoryAction.ALIAS_ADDED
    assert entry.current_value == "Nome alternativo"
    assert dict(entry.metadata or {}) == {
        "source": "database",
    }


def test_equal_history_entries_are_equal() -> None:
    person_id = PersonId.new()
    occurred_at = utc_datetime()

    first = PersonHistoryEntry.create(
        person_id=person_id,
        action=PeopleHistoryAction.PERSON_CREATED,
        occurred_at=occurred_at,
        metadata={"source": "api"},
    )

    second = PersonHistoryEntry.create(
        person_id=person_id,
        action=PeopleHistoryAction.PERSON_CREATED,
        occurred_at=occurred_at,
        metadata={"source": "api"},
    )

    assert first == second
    assert hash(first) == hash(second)


def test_different_history_entries_are_not_equal() -> None:
    first = make_entry()
    second = make_entry()

    assert first != second


def test_history_entry_is_not_equal_to_other_type() -> None:
    assert make_entry() != object()


def test_history_entry_is_immutable() -> None:
    entry = make_entry()

    with pytest.raises(FrozenInstanceError):
        entry.current_value = "Alterado"