"""Testes do histórico imutável do contexto competitivo."""

from dataclasses import FrozenInstanceError

import pytest

from ultrastats_ai.domain.competition import (
    CompetitionChangeType,
    CompetitionEntityKind,
    CompetitionFieldChange,
    CompetitionHistoryEntry,
    DuplicateHistoryFieldError,
    EmptyHistoryChangesError,
)
from ultrastats_ai.domain.shared import (
    CanonicalId,
    CompetitionId,
    UtcTimestamp,
)


def make_history_entry(
    *,
    id: CanonicalId | None = None,
    entity_id: CanonicalId | None = None,
    entity_kind: CompetitionEntityKind = (
        CompetitionEntityKind.COMPETITION
    ),
    change_type: CompetitionChangeType = (
        CompetitionChangeType.CREATED
    ),
    occurred_at: UtcTimestamp | None = None,
    changes: tuple[CompetitionFieldChange, ...] = (),
) -> CompetitionHistoryEntry:
    """Cria uma entrada válida para os testes."""

    return CompetitionHistoryEntry(
        id=id or CompetitionId.new(),
        entity_id=entity_id or CompetitionId.new(),
        entity_kind=entity_kind,
        change_type=change_type,
        occurred_at=occurred_at
        or UtcTimestamp("2026-07-22T12:00:00Z"),
        changes=changes,
    )


# ============================================================
# CompetitionEntityKind e CompetitionChangeType
# ============================================================


def test_competition_entity_kind_values_are_stable() -> None:
    assert CompetitionEntityKind.COMPETITION.value == (
        "competition"
    )
    assert CompetitionEntityKind.SEASON.value == "season"
    assert CompetitionEntityKind.STAGE.value == "stage"
    assert CompetitionEntityKind.ROUND.value == "round"
    assert CompetitionEntityKind.TIE.value == "tie"


def test_competition_change_type_values_are_stable() -> None:
    assert CompetitionChangeType.CREATED.value == "created"
    assert CompetitionChangeType.UPDATED.value == "updated"
    assert CompetitionChangeType.DELETED.value == "deleted"


# ============================================================
# CompetitionFieldChange — criação e normalização
# ============================================================


def test_field_change_is_created_with_valid_values() -> None:
    change = CompetitionFieldChange(
        field_name="name",
        previous_value="Nome antigo",
        current_value="Nome novo",
    )

    assert change.field_name == "name"
    assert change.previous_value == "Nome antigo"
    assert change.current_value == "Nome novo"


def test_field_change_accepts_creation() -> None:
    change = CompetitionFieldChange(
        field_name="country_id",
        previous_value=None,
        current_value="BRA",
    )

    assert change.previous_value is None
    assert change.current_value == "BRA"


def test_field_change_accepts_removal() -> None:
    change = CompetitionFieldChange(
        field_name="country_id",
        previous_value="BRA",
        current_value=None,
    )

    assert change.previous_value == "BRA"
    assert change.current_value is None


def test_field_change_normalizes_surrounding_spaces() -> None:
    change = CompetitionFieldChange(
        field_name="  name  ",
        previous_value="  Nome antigo  ",
        current_value="  Nome novo  ",
    )

    assert change.field_name == "name"
    assert change.previous_value == "Nome antigo"
    assert change.current_value == "Nome novo"


def test_field_change_preserves_none_during_normalization() -> None:
    creation = CompetitionFieldChange(
        field_name="name",
        previous_value=None,
        current_value="Valor",
    )

    removal = CompetitionFieldChange(
        field_name="name",
        previous_value="Valor",
        current_value=None,
    )

    assert creation.previous_value is None
    assert removal.current_value is None


# ============================================================
# CompetitionFieldChange — validações
# ============================================================


def test_field_change_rejects_invalid_field_name_type() -> None:
    with pytest.raises(
        TypeError,
        match="field_name deve ser string",
    ):
        CompetitionFieldChange(
            field_name=123,
            previous_value=None,
            current_value="valor",
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "",
        " ",
        "\t",
        "\n",
        "   \t   ",
    ],
)
def test_field_change_rejects_empty_field_name(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="field_name não pode ser vazio",
    ):
        CompetitionFieldChange(
            field_name=field_name,
            previous_value=None,
            current_value="valor",
        )


@pytest.mark.parametrize(
    "previous_value",
    [
        1,
        True,
        1.5,
        object(),
    ],
)
def test_field_change_rejects_invalid_previous_value_type(
    previous_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "previous_value deve ser string ou None"
        ),
    ):
        CompetitionFieldChange(
            field_name="name",
            previous_value=previous_value,
            current_value="novo",
        )


@pytest.mark.parametrize(
    "current_value",
    [
        1,
        True,
        1.5,
        object(),
    ],
)
def test_field_change_rejects_invalid_current_value_type(
    current_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "current_value deve ser string ou None"
        ),
    ):
        CompetitionFieldChange(
            field_name="name",
            previous_value="antigo",
            current_value=current_value,
        )


@pytest.mark.parametrize(
    ("previous_value", "current_value"),
    [
        ("valor", "valor"),
        (" valor ", "valor"),
        ("valor", " valor "),
        (" valor ", " valor "),
        ("", ""),
        (" ", ""),
        (None, None),
    ],
)
def test_field_change_rejects_equal_normalized_values(
    previous_value: str | None,
    current_value: str | None,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "previous_value e current_value "
            "devem ser diferentes"
        ),
    ):
        CompetitionFieldChange(
            field_name="name",
            previous_value=previous_value,
            current_value=current_value,
        )


def test_field_change_is_immutable() -> None:
    change = CompetitionFieldChange(
        field_name="name",
        previous_value="antigo",
        current_value="novo",
    )

    with pytest.raises(FrozenInstanceError):
        change.field_name = "code"


# ============================================================
# CompetitionHistoryEntry — criação
# ============================================================


def test_history_entry_is_created_without_changes() -> None:
    entry = make_history_entry()

    assert isinstance(entry.id, CanonicalId)
    assert isinstance(entry.entity_id, CanonicalId)
    assert entry.entity_kind is (
        CompetitionEntityKind.COMPETITION
    )
    assert entry.change_type is CompetitionChangeType.CREATED
    assert entry.changes == ()


def test_created_entry_accepts_changes() -> None:
    change = CompetitionFieldChange(
        field_name="name",
        previous_value=None,
        current_value="Brasileirão",
    )

    entry = make_history_entry(
        change_type=CompetitionChangeType.CREATED,
        changes=(change,),
    )

    assert entry.changes == (change,)


def test_deleted_entry_accepts_empty_changes() -> None:
    entry = make_history_entry(
        change_type=CompetitionChangeType.DELETED,
    )

    assert entry.changes == ()


def test_updated_entry_accepts_changes() -> None:
    change = CompetitionFieldChange(
        field_name="name",
        previous_value="Nome antigo",
        current_value="Nome novo",
    )

    entry = make_history_entry(
        change_type=CompetitionChangeType.UPDATED,
        changes=(change,),
    )

    assert entry.change_type is CompetitionChangeType.UPDATED
    assert entry.changes == (change,)


def test_history_entry_returns_changed_fields() -> None:
    first = CompetitionFieldChange(
        field_name="name",
        previous_value="Antigo",
        current_value="Novo",
    )

    second = CompetitionFieldChange(
        field_name="code",
        previous_value="OLD",
        current_value="NEW",
    )

    entry = make_history_entry(
        change_type=CompetitionChangeType.UPDATED,
        changes=(first, second),
    )

    assert entry.changed_fields == (
        "name",
        "code",
    )


def test_history_entry_changed_fields_is_empty() -> None:
    entry = make_history_entry()

    assert entry.changed_fields == ()


def test_history_entry_is_immutable() -> None:
    entry = make_history_entry()

    with pytest.raises(FrozenInstanceError):
        entry.changes = ()


# ============================================================
# CompetitionHistoryEntry — validações de tipos
# ============================================================


def test_history_entry_rejects_invalid_id_type() -> None:
    with pytest.raises(
        TypeError,
        match="id deve ser CanonicalId",
    ):
        make_history_entry(id="invalid")


def test_history_entry_rejects_invalid_entity_id_type() -> None:
    with pytest.raises(
        TypeError,
        match="entity_id deve ser CanonicalId",
    ):
        make_history_entry(entity_id="invalid")


def test_history_entry_rejects_invalid_entity_kind_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "entity_kind deve ser "
            "CompetitionEntityKind"
        ),
    ):
        make_history_entry(
            entity_kind="competition",
        )


def test_history_entry_rejects_invalid_change_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "change_type deve ser "
            "CompetitionChangeType"
        ),
    ):
        make_history_entry(
            change_type="created",
        )


def test_history_entry_rejects_invalid_occurred_at() -> None:
    with pytest.raises(
        TypeError,
        match="occurred_at deve ser UtcTimestamp",
    ):
        make_history_entry(
            occurred_at="2026-07-22T12:00:00Z",
        )


@pytest.mark.parametrize(
    "changes",
    [
        [],
        set(),
        {},
        "invalid",
        b"invalid",
    ],
)
def test_history_entry_rejects_non_tuple_changes(
    changes: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="changes deve ser tuple",
    ):
        make_history_entry(changes=changes)


def test_history_entry_rejects_invalid_change_item() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "changes deve conter "
            "CompetitionFieldChange"
        ),
    ):
        make_history_entry(
            changes=("invalid",),
        )


# ============================================================
# CompetitionHistoryEntry — invariantes
# ============================================================


def test_history_entry_rejects_duplicate_field_names() -> None:
    first = CompetitionFieldChange(
        field_name="name",
        previous_value="A",
        current_value="B",
    )

    second = CompetitionFieldChange(
        field_name="name",
        previous_value="B",
        current_value="C",
    )

    with pytest.raises(
        DuplicateHistoryFieldError,
        match="Um campo não pode aparecer duas vezes",
    ):
        make_history_entry(
            change_type=CompetitionChangeType.UPDATED,
            changes=(first, second),
        )


def test_history_entry_detects_duplicate_fields_case_insensitively(
) -> None:
    first = CompetitionFieldChange(
        field_name="Name",
        previous_value="A",
        current_value="B",
    )

    second = CompetitionFieldChange(
        field_name="NAME",
        previous_value="B",
        current_value="C",
    )

    with pytest.raises(DuplicateHistoryFieldError):
        make_history_entry(
            change_type=CompetitionChangeType.UPDATED,
            changes=(first, second),
        )


def test_history_entry_accepts_distinct_field_names() -> None:
    first = CompetitionFieldChange(
        field_name="name",
        previous_value="A",
        current_value="B",
    )

    second = CompetitionFieldChange(
        field_name="code",
        previous_value="OLD",
        current_value="NEW",
    )

    entry = make_history_entry(
        change_type=CompetitionChangeType.UPDATED,
        changes=(first, second),
    )

    assert len(entry.changes) == 2


def test_updated_history_entry_requires_changes() -> None:
    with pytest.raises(
        EmptyHistoryChangesError,
        match=(
            "Uma atualização deve possuir alterações"
        ),
    ):
        make_history_entry(
            change_type=CompetitionChangeType.UPDATED,
            changes=(),
        )


# ============================================================
# CompetitionHistoryEntry.from_iterable
# ============================================================


def test_history_entry_is_created_from_list() -> None:
    change = CompetitionFieldChange(
        field_name="name",
        previous_value="A",
        current_value="B",
    )

    entry = CompetitionHistoryEntry.from_iterable(
        id=CompetitionId.new(),
        entity_id=CompetitionId.new(),
        entity_kind=CompetitionEntityKind.COMPETITION,
        change_type=CompetitionChangeType.UPDATED,
        occurred_at=UtcTimestamp(
            "2026-07-22T12:00:00Z"
        ),
        changes=[change],
    )

    assert entry.changes == (change,)
    assert isinstance(entry.changes, tuple)


def test_history_entry_is_created_from_generator() -> None:
    changes = (
        CompetitionFieldChange(
            field_name=field_name,
            previous_value="old",
            current_value="new",
        )
        for field_name in (
            "name",
            "code",
        )
    )

    entry = CompetitionHistoryEntry.from_iterable(
        id=CompetitionId.new(),
        entity_id=CompetitionId.new(),
        entity_kind=CompetitionEntityKind.COMPETITION,
        change_type=CompetitionChangeType.UPDATED,
        occurred_at=UtcTimestamp(
            "2026-07-22T12:00:00Z"
        ),
        changes=changes,
    )

    assert entry.changed_fields == (
        "name",
        "code",
    )


def test_history_entry_from_iterable_accepts_empty_iterable_for_created(
) -> None:
    entry = CompetitionHistoryEntry.from_iterable(
        id=CompetitionId.new(),
        entity_id=CompetitionId.new(),
        entity_kind=CompetitionEntityKind.COMPETITION,
        change_type=CompetitionChangeType.CREATED,
        occurred_at=UtcTimestamp(
            "2026-07-22T12:00:00Z"
        ),
        changes=(),
    )

    assert entry.changes == ()


@pytest.mark.parametrize(
    "changes",
    [
        "invalid",
        b"invalid",
    ],
)
def test_history_entry_from_iterable_rejects_text(
    changes: str | bytes,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "changes deve ser um iterável de "
            "CompetitionFieldChange"
        ),
    ):
        CompetitionHistoryEntry.from_iterable(
            id=CompetitionId.new(),
            entity_id=CompetitionId.new(),
            entity_kind=(
                CompetitionEntityKind.COMPETITION
            ),
            change_type=CompetitionChangeType.CREATED,
            occurred_at=UtcTimestamp(
                "2026-07-22T12:00:00Z"
            ),
            changes=changes,
        )