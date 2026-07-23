"""Testes da entidade canônica Stage."""

from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from ultrastats_ai.domain.competition import (
    CompetitionAliases,
    Stage,
)
from ultrastats_ai.domain.shared import (
    AliasValue,
    DomainDate,
    Name,
    PhaseType,
    StageId,
)


_UNSET = object()


def make_stage(
    season,
    *,
    id: Any = _UNSET,
    season_value: Any = _UNSET,
    name: Any = _UNSET,
    phase_type: Any = _UNSET,
    sequence: Any = _UNSET,
    start_date: Any = _UNSET,
    end_date: Any = _UNSET,
    aliases: Any = _UNSET,
    is_active: Any = True,
) -> Stage:
    """Cria uma fase válida com campos sobrescrevíveis."""

    return Stage(
        id=(
            StageId.new()
            if id is _UNSET
            else id
        ),
        season=(
            season
            if season_value is _UNSET
            else season_value
        ),
        name=(
            Name("Fase de grupos")
            if name is _UNSET
            else name
        ),
        phase_type=(
            PhaseType.GROUP_STAGE
            if phase_type is _UNSET
            else phase_type
        ),
        sequence=(
            None
            if sequence is _UNSET
            else sequence
        ),
        start_date=(
            None
            if start_date is _UNSET
            else start_date
        ),
        end_date=(
            None
            if end_date is _UNSET
            else end_date
        ),
        aliases=(
            CompetitionAliases.empty()
            if aliases is _UNSET
            else aliases
        ),
        is_active=is_active,
    )


# ============================================================
# Criação
# ============================================================


def test_stage_is_created_with_required_fields(
    season,
) -> None:
    stage = make_stage(season)

    assert isinstance(stage.id, StageId)
    assert stage.season == season
    assert stage.season_id == season.id
    assert stage.competition_id == season.competition.id
    assert stage.name == Name("Fase de grupos")
    assert stage.phase_type is PhaseType.GROUP_STAGE
    assert stage.sequence is None
    assert stage.start_date is None
    assert stage.end_date is None
    assert stage.aliases == CompetitionAliases.empty()
    assert stage.is_active is True


def test_stage_accepts_optional_fields(
    season,
) -> None:
    aliases = CompetitionAliases(
        (
            AliasValue("Grupos"),
            AliasValue("Primeira fase"),
        )
    )

    stage = make_stage(
        season,
        sequence=1,
        start_date=DomainDate("2026-01-01"),
        end_date=DomainDate("2026-03-31"),
        aliases=aliases,
        is_active=False,
    )

    assert stage.sequence == 1
    assert stage.start_date == DomainDate(
        "2026-01-01"
    )
    assert stage.end_date == DomainDate(
        "2026-03-31"
    )
    assert stage.aliases == aliases
    assert stage.is_active is False


# ============================================================
# Validações do construtor
# ============================================================


def test_stage_rejects_invalid_id_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="id deve ser StageId",
    ):
        make_stage(
            season,
            id="invalid",
        )


def test_stage_rejects_invalid_season_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="season deve ser Season",
    ):
        make_stage(
            season,
            season_value="invalid",
        )


def test_stage_rejects_invalid_name_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="name deve ser Name",
    ):
        make_stage(
            season,
            name="Fase de grupos",
        )


def test_stage_rejects_invalid_phase_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="phase_type deve ser PhaseType",
    ):
        make_stage(
            season,
            phase_type="group_stage",
        )


@pytest.mark.parametrize(
    "invalid_sequence",
    [
        True,
        False,
        1.5,
        "1",
        object(),
    ],
)
def test_stage_rejects_invalid_sequence_type(
    season,
    invalid_sequence: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="sequence deve ser int ou None",
    ):
        make_stage(
            season,
            sequence=invalid_sequence,
        )


@pytest.mark.parametrize(
    "invalid_sequence",
    [
        0,
        -1,
        -10,
    ],
)
def test_stage_rejects_non_positive_sequence(
    season,
    invalid_sequence: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "sequence deve ser maior ou igual a 1"
        ),
    ):
        make_stage(
            season,
            sequence=invalid_sequence,
        )


def test_stage_accepts_positive_sequence(
    season,
) -> None:
    stage = make_stage(
        season,
        sequence=1,
    )

    assert stage.sequence == 1


@pytest.mark.parametrize(
    "invalid_start_date",
    [
        "2026-01-01",
        20260101,
        True,
        object(),
    ],
)
def test_stage_rejects_invalid_start_date_type(
    season,
    invalid_start_date: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "start_date deve ser DomainDate ou None"
        ),
    ):
        make_stage(
            season,
            start_date=invalid_start_date,
        )


@pytest.mark.parametrize(
    "invalid_end_date",
    [
        "2026-12-31",
        20261231,
        True,
        object(),
    ],
)
def test_stage_rejects_invalid_end_date_type(
    season,
    invalid_end_date: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "end_date deve ser DomainDate ou None"
        ),
    ):
        make_stage(
            season,
            end_date=invalid_end_date,
        )


def test_stage_rejects_inverted_period(
    season,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "start_date deve ser anterior ou igual "
            "a end_date"
        ),
    ):
        make_stage(
            season,
            start_date=DomainDate("2026-03-31"),
            end_date=DomainDate("2026-01-01"),
        )


def test_stage_accepts_equal_start_and_end_dates(
    season,
) -> None:
    date = DomainDate("2026-01-01")

    stage = make_stage(
        season,
        start_date=date,
        end_date=date,
    )

    assert stage.start_date == date
    assert stage.end_date == date


def test_stage_accepts_only_start_date(
    season,
) -> None:
    stage = make_stage(
        season,
        start_date=DomainDate("2026-01-01"),
    )

    assert stage.start_date == DomainDate(
        "2026-01-01"
    )
    assert stage.end_date is None


def test_stage_accepts_only_end_date(
    season,
) -> None:
    stage = make_stage(
        season,
        end_date=DomainDate("2026-03-31"),
    )

    assert stage.start_date is None
    assert stage.end_date == DomainDate(
        "2026-03-31"
    )


def test_stage_rejects_invalid_aliases_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="aliases deve ser CompetitionAliases",
    ):
        make_stage(
            season,
            aliases=(AliasValue("Grupos"),),
        )


@pytest.mark.parametrize(
    "invalid_is_active",
    [
        1,
        0,
        "true",
        None,
    ],
)
def test_stage_rejects_invalid_is_active_type(
    season,
    invalid_is_active: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="is_active deve ser bool",
    ):
        make_stage(
            season,
            is_active=invalid_is_active,
        )


# ============================================================
# Alterações imutáveis
# ============================================================


def test_stage_rename_returns_new_instance(
    stage,
) -> None:
    updated = stage.rename(
        Name("Mata-mata")
    )

    assert updated is not stage
    assert updated == stage
    assert updated.name == Name("Mata-mata")
    assert stage.name == Name("Fase de grupos")


def test_stage_rename_rejects_invalid_type(
    stage,
) -> None:
    with pytest.raises(
        TypeError,
        match="name deve ser Name",
    ):
        stage.rename("Mata-mata")


def test_stage_reorder_returns_new_instance(
    stage,
) -> None:
    updated = stage.reorder(2)

    assert updated is not stage
    assert updated == stage
    assert updated.sequence == 2
    assert stage.sequence == 1


def test_stage_reorder_accepts_none(
    stage,
) -> None:
    updated = stage.reorder(None)

    assert updated is not stage
    assert updated.sequence is None
    assert stage.sequence == 1


def test_stage_reorder_reuses_constructor_validation(
    stage,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "sequence deve ser maior ou igual a 1"
        ),
    ):
        stage.reorder(0)


def test_stage_change_period_returns_new_instance(
    stage,
) -> None:
    updated = stage.change_period(
        start_date=DomainDate("2026-01-01"),
        end_date=DomainDate("2026-02-01"),
    )

    assert updated is not stage
    assert updated == stage
    assert updated.start_date == DomainDate(
        "2026-01-01"
    )
    assert updated.end_date == DomainDate(
        "2026-02-01"
    )


def test_stage_change_period_accepts_open_start(
    stage,
) -> None:
    updated = stage.change_period(
        start_date=None,
        end_date=DomainDate("2026-02-01"),
    )

    assert updated.start_date is None
    assert updated.end_date == DomainDate(
        "2026-02-01"
    )


def test_stage_change_period_accepts_open_end(
    stage,
) -> None:
    updated = stage.change_period(
        start_date=DomainDate("2026-01-01"),
        end_date=None,
    )

    assert updated.start_date == DomainDate(
        "2026-01-01"
    )
    assert updated.end_date is None


def test_stage_change_period_rejects_inverted_period(
    stage,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "start_date deve ser anterior ou igual "
            "a end_date"
        ),
    ):
        stage.change_period(
            start_date=DomainDate("2026-02-01"),
            end_date=DomainDate("2026-01-01"),
        )


# ============================================================
# Aliases
# ============================================================


def test_stage_adds_alias_immutably(
    stage,
) -> None:
    alias = AliasValue("Grupos")

    updated = stage.add_alias(alias)

    assert updated is not stage
    assert updated == stage
    assert alias in updated.aliases
    assert alias not in stage.aliases


def test_stage_removes_alias_immutably(
    season,
) -> None:
    alias = AliasValue("Grupos")

    stage = make_stage(
        season,
        aliases=CompetitionAliases((alias,)),
    )

    updated = stage.remove_alias(alias)

    assert updated is not stage
    assert updated == stage
    assert alias not in updated.aliases
    assert alias in stage.aliases


# ============================================================
# Estado de atividade
# ============================================================


def test_stage_can_be_deactivated(
    stage,
) -> None:
    updated = stage.deactivate()

    assert updated is not stage
    assert updated == stage
    assert updated.is_active is False
    assert stage.is_active is True


def test_stage_can_be_reactivated(
    stage,
) -> None:
    inactive = stage.deactivate()

    updated = inactive.activate()

    assert updated is not inactive
    assert updated == inactive
    assert updated.is_active is True
    assert inactive.is_active is False


# ============================================================
# Identidade
# ============================================================


def test_stage_is_compared_by_identity(
    stage,
) -> None:
    renamed = stage.rename(
        Name("Novo nome")
    )

    assert renamed == stage
    assert hash(renamed) == hash(stage)


def test_stages_with_different_ids_are_not_equal(
    season,
    stage,
) -> None:
    other = make_stage(season)

    assert other != stage


def test_stage_equality_returns_not_equal_for_other_type(
    stage,
) -> None:
    assert stage != object()


def test_stage_hash_is_based_on_id(
    stage,
) -> None:
    assert hash(stage) == hash(stage.id)


# ============================================================
# Imutabilidade
# ============================================================


def test_stage_is_immutable(
    stage,
) -> None:
    with pytest.raises(FrozenInstanceError):
        stage.sequence = 10