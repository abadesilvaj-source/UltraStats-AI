"""Testes dos objetos de histórico geográfico."""

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from ultrastats_ai.domain.geography import (
    DuplicateHistoryFieldError,
    EmptyHistoryChangesError,
    GeographyChangeType,
    GeographyEntityKind,
    GeographyFieldChange,
    GeographyHistoryEntry,
)
from ultrastats_ai.domain.shared import (
    CanonicalId,
    UtcTimestamp,
)


def test_geography_enum_string_values_are_canonical() -> None:
    assert str(GeographyEntityKind.CITY) == "city"
    assert str(GeographyChangeType.UPDATED) == "updated"


def make_history_id(
    value: str = "00000000-0000-0000-0000-000000100001",
) -> CanonicalId:
    """Cria uma identidade determinística de histórico."""
    return CanonicalId(UUID(value))


def make_entity_id(
    value: str = "00000000-0000-0000-0000-000000001001",
) -> CanonicalId:
    """Cria uma identidade determinística de entidade."""
    return CanonicalId(UUID(value))


def make_timestamp() -> UtcTimestamp:
    """Cria um timestamp determinístico."""
    return UtcTimestamp("2026-07-22T12:00:00Z")


def make_field_change() -> GeographyFieldChange:
    """Cria uma alteração válida."""
    return GeographyFieldChange(
        field_name="name",
        previous_value="Araraquara",
        current_value="Morada do Sol",
    )


def make_history_entry(
    *,
    change_type: GeographyChangeType = GeographyChangeType.UPDATED,
    changes: tuple[GeographyFieldChange, ...] | None = None,
) -> GeographyHistoryEntry:
    """Cria uma entrada de histórico válida."""
    return GeographyHistoryEntry(
        id=make_history_id(),
        entity_id=make_entity_id(),
        entity_kind=GeographyEntityKind.CITY,
        change_type=change_type,
        occurred_at=make_timestamp(),
        changes=(
            changes
            if changes is not None
            else (make_field_change(),)
        ),
    )


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("country", GeographyEntityKind.COUNTRY),
        (" REGION ", GeographyEntityKind.REGION),
        ("City", GeographyEntityKind.CITY),
        ("stadium", GeographyEntityKind.STADIUM),
    ],
)
def test_geography_entity_kind_parse(
    raw_value: str,
    expected: GeographyEntityKind,
) -> None:
    assert GeographyEntityKind.parse(raw_value) is expected


def test_geography_entity_kind_parse_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="desconhecido"):
        GeographyEntityKind.parse("continent")


def test_geography_entity_kind_parse_rejects_invalid_type() -> None:
    with pytest.raises(TypeError, match="string"):
        GeographyEntityKind.parse(1)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("created", GeographyChangeType.CREATED),
        (" UPDATED ", GeographyChangeType.UPDATED),
        ("Deleted", GeographyChangeType.DELETED),
    ],
)
def test_geography_change_type_parse(
    raw_value: str,
    expected: GeographyChangeType,
) -> None:
    assert GeographyChangeType.parse(raw_value) is expected


def test_geography_change_type_parse_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="desconhecido"):
        GeographyChangeType.parse("restored")


def test_geography_change_type_parse_rejects_invalid_type() -> None:
    with pytest.raises(TypeError, match="string"):
        GeographyChangeType.parse(None)  # type: ignore[arg-type]


def test_field_change_is_created() -> None:
    change = GeographyFieldChange(
        field_name=" name ",
        previous_value=" Araraquara ",
        current_value=" Morada do Sol ",
    )

    assert change.field_name == "name"
    assert change.previous_value == "Araraquara"
    assert change.current_value == "Morada do Sol"


def test_field_change_detects_creation() -> None:
    change = GeographyFieldChange(
        field_name="coordinates",
        previous_value=None,
        current_value="-21.7845,-48.1780",
    )

    assert change.is_creation
    assert not change.is_removal
    assert not change.is_update


def test_field_change_detects_removal() -> None:
    change = GeographyFieldChange(
        field_name="coordinates",
        previous_value="-21.7845,-48.1780",
        current_value=None,
    )

    assert not change.is_creation
    assert change.is_removal
    assert not change.is_update


def test_field_change_detects_update() -> None:
    change = make_field_change()

    assert not change.is_creation
    assert not change.is_removal
    assert change.is_update


def test_field_change_rejects_empty_field_name() -> None:
    with pytest.raises(ValueError, match="vazio"):
        GeographyFieldChange(
            field_name="   ",
            previous_value="old",
            current_value="new",
        )


def test_field_change_rejects_invalid_field_name_type() -> None:
    with pytest.raises(TypeError, match="field_name"):
        GeographyFieldChange(
            field_name=10,  # type: ignore[arg-type]
            previous_value="old",
            current_value="new",
        )


def test_field_change_rejects_invalid_previous_value_type() -> None:
    with pytest.raises(TypeError, match="previous_value"):
        GeographyFieldChange(
            field_name="name",
            previous_value=10,  # type: ignore[arg-type]
            current_value="new",
        )


def test_field_change_rejects_invalid_current_value_type() -> None:
    with pytest.raises(TypeError, match="current_value"):
        GeographyFieldChange(
            field_name="name",
            previous_value="old",
            current_value=10,  # type: ignore[arg-type]
        )


def test_field_change_rejects_equal_values() -> None:
    with pytest.raises(ValueError, match="diferentes"):
        GeographyFieldChange(
            field_name="name",
            previous_value="Araraquara",
            current_value="Araraquara",
        )


def test_history_entry_is_created() -> None:
    entry = make_history_entry()

    assert entry.id == make_history_id()
    assert entry.entity_id == make_entity_id()
    assert entry.entity_kind is GeographyEntityKind.CITY
    assert entry.change_type is GeographyChangeType.UPDATED
    assert entry.occurred_at == make_timestamp()
    assert len(entry.changes) == 1


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_message"),
    [
        ("id", "invalid", "CanonicalId"),
        ("entity_id", "invalid", "CanonicalId"),
        (
            "entity_kind",
            "city",
            "GeographyEntityKind",
        ),
        (
            "change_type",
            "updated",
            "GeographyChangeType",
        ),
        (
            "occurred_at",
            "2026-07-22T12:00:00Z",
            "UtcTimestamp",
        ),
        ("changes", [], "tuple"),
    ],
)
def test_history_entry_rejects_invalid_types(
    field_name: str,
    invalid_value: object,
    expected_message: str,
) -> None:
    values: dict[str, object] = {
        "id": make_history_id(),
        "entity_id": make_entity_id(),
        "entity_kind": GeographyEntityKind.CITY,
        "change_type": GeographyChangeType.UPDATED,
        "occurred_at": make_timestamp(),
        "changes": (make_field_change(),),
    }

    values[field_name] = invalid_value

    with pytest.raises(TypeError, match=expected_message):
        GeographyHistoryEntry(**values)  # type: ignore[arg-type]


def test_history_entry_rejects_invalid_change_item() -> None:
    with pytest.raises(TypeError, match="GeographyFieldChange"):
        GeographyHistoryEntry(
            id=make_history_id(),
            entity_id=make_entity_id(),
            entity_kind=GeographyEntityKind.CITY,
            change_type=GeographyChangeType.UPDATED,
            occurred_at=make_timestamp(),
            changes=("name",),  # type: ignore[arg-type]
        )


def test_updated_history_requires_changes() -> None:
    with pytest.raises(EmptyHistoryChangesError):
        make_history_entry(
            change_type=GeographyChangeType.UPDATED,
            changes=(),
        )


def test_created_history_can_have_empty_changes() -> None:
    entry = make_history_entry(
        change_type=GeographyChangeType.CREATED,
        changes=(),
    )

    assert entry.changes == ()


def test_deleted_history_can_have_empty_changes() -> None:
    entry = make_history_entry(
        change_type=GeographyChangeType.DELETED,
        changes=(),
    )

    assert entry.changes == ()


def test_history_entry_rejects_duplicate_fields() -> None:
    first = GeographyFieldChange(
        field_name="name",
        previous_value="A",
        current_value="B",
    )

    second = GeographyFieldChange(
        field_name="NAME",
        previous_value="B",
        current_value="C",
    )

    with pytest.raises(DuplicateHistoryFieldError):
        make_history_entry(
            changes=(first, second),
        )


def test_history_entry_from_iterable_converts_to_tuple() -> None:
    change = make_field_change()

    entry = GeographyHistoryEntry.from_iterable(
        id=make_history_id(),
        entity_id=make_entity_id(),
        entity_kind=GeographyEntityKind.CITY,
        change_type=GeographyChangeType.UPDATED,
        occurred_at=make_timestamp(),
        changes=[change],
    )

    assert entry.changes == (change,)
    assert isinstance(entry.changes, tuple)


def test_history_entry_from_iterable_rejects_string() -> None:
    with pytest.raises(TypeError, match="iterável"):
        GeographyHistoryEntry.from_iterable(
            id=make_history_id(),
            entity_id=make_entity_id(),
            entity_kind=GeographyEntityKind.CITY,
            change_type=GeographyChangeType.UPDATED,
            occurred_at=make_timestamp(),
            changes="name",  # type: ignore[arg-type]
        )


def test_changed_fields_returns_field_names() -> None:
    first = GeographyFieldChange(
        field_name="name",
        previous_value="A",
        current_value="B",
    )

    second = GeographyFieldChange(
        field_name="coordinates",
        previous_value=None,
        current_value="-21,-48",
    )

    entry = make_history_entry(
        changes=(first, second),
    )

    assert entry.changed_fields == (
        "name",
        "coordinates",
    )


def test_has_changed_field_is_case_insensitive() -> None:
    entry = make_history_entry()

    assert entry.has_changed_field("NAME")
    assert entry.has_changed_field(" name ")
    assert not entry.has_changed_field("coordinates")


def test_has_changed_field_returns_false_for_invalid_type() -> None:
    entry = make_history_entry()

    assert not entry.has_changed_field(10)  # type: ignore[arg-type]


def test_get_change_returns_expected_change() -> None:
    change = make_field_change()
    entry = make_history_entry(changes=(change,))

    result = entry.get_change("NAME")

    assert result == change


def test_get_change_returns_none_for_unknown_field() -> None:
    entry = make_history_entry()

    assert entry.get_change("coordinates") is None


def test_get_change_returns_none_for_invalid_type() -> None:
    entry = make_history_entry()

    assert entry.get_change(None) is None  # type: ignore[arg-type]


def test_field_change_is_immutable() -> None:
    change = make_field_change()

    with pytest.raises(FrozenInstanceError):
        change.field_name = "other"  # type: ignore[misc]


def test_history_entry_is_immutable() -> None:
    entry = make_history_entry()

    with pytest.raises(FrozenInstanceError):
        entry.changes = ()  # type: ignore[misc]
