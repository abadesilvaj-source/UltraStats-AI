"""Testes da entidade canônica Round."""

from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from ultrastats_ai.domain.competition import (
    Competition,
    CompetitionAliases,
    CompetitionHierarchyError,
    Round,
    Season,
    Stage,
)
from ultrastats_ai.domain.shared import (
    AliasValue,
    CompetitionCode,
    CompetitionId,
    CompetitionName,
    CompetitionType,
    DomainDate,
    Name,
    PhaseType,
    RoundId,
    RoundNumber,
    RoundType,
    SeasonId,
    StageId,
)


_UNSET = object()


def make_round(
    season,
    *,
    id: Any = _UNSET,
    season_value: Any = _UNSET,
    name: Any = _UNSET,
    round_type: Any = _UNSET,
    stage: Any = _UNSET,
    round_number: Any = _UNSET,
    sequence: Any = _UNSET,
    start_date: Any = _UNSET,
    end_date: Any = _UNSET,
    aliases: Any = _UNSET,
    is_current: Any = False,
    is_active: Any = True,
) -> Round:
    """Cria uma rodada válida com campos sobrescrevíveis."""

    return Round(
        id=(
            RoundId.new()
            if id is _UNSET
            else id
        ),
        season=(
            season
            if season_value is _UNSET
            else season_value
        ),
        name=(
            Name("Rodada 1")
            if name is _UNSET
            else name
        ),
        round_type=(
            RoundType.REGULAR
            if round_type is _UNSET
            else round_type
        ),
        stage=(
            None
            if stage is _UNSET
            else stage
        ),
        round_number=(
            None
            if round_number is _UNSET
            else round_number
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
        is_current=is_current,
        is_active=is_active,
    )


def make_other_season() -> Season:
    """Cria uma temporada pertencente a outra competição."""

    competition = Competition(
        id=CompetitionId.new(),
        code=CompetitionCode("OUT"),
        name=CompetitionName("Outra competição"),
        competition_type=CompetitionType.CUP,
    )

    return Season(
        id=SeasonId.new(),
        competition=competition,
        name=Name("2026"),
    )


def make_stage_for_season(
    season: Season,
) -> Stage:
    """Cria uma fase vinculada à temporada informada."""

    return Stage(
        id=StageId.new(),
        season=season,
        name=Name("Fase"),
        phase_type=PhaseType.GROUP_STAGE,
    )


# ============================================================
# Criação
# ============================================================


def test_round_is_created_with_required_fields(
    season,
) -> None:
    round_ = make_round(season)

    assert isinstance(round_.id, RoundId)
    assert round_.season == season
    assert round_.competition_id == season.competition.id
    assert round_.season_id == season.id
    assert round_.name == Name("Rodada 1")
    assert round_.round_type is RoundType.REGULAR
    assert round_.stage is None
    assert round_.stage_id is None
    assert round_.round_number is None
    assert round_.sequence is None
    assert round_.start_date is None
    assert round_.end_date is None
    assert round_.aliases == CompetitionAliases.empty()
    assert round_.is_current is False
    assert round_.is_active is True


def test_round_accepts_optional_fields(
    season,
    stage,
) -> None:
    aliases = CompetitionAliases(
        (
            AliasValue("Primeira rodada"),
            AliasValue("R1"),
        )
    )

    round_ = make_round(
        season,
        round_type=RoundType.GROUP,
        stage=stage,
        round_number=RoundNumber(1),
        sequence=1,
        start_date=DomainDate("2026-01-01"),
        end_date=DomainDate("2026-01-02"),
        aliases=aliases,
        is_current=True,
        is_active=False,
    )

    assert round_.stage == stage
    assert round_.stage_id == stage.id
    assert round_.round_number == RoundNumber(1)
    assert round_.sequence == 1
    assert round_.start_date == DomainDate(
        "2026-01-01"
    )
    assert round_.end_date == DomainDate(
        "2026-01-02"
    )
    assert round_.aliases == aliases
    assert round_.is_current is True
    assert round_.is_active is False


# ============================================================
# Validações básicas
# ============================================================


def test_round_rejects_invalid_id_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="id deve ser RoundId",
    ):
        make_round(
            season,
            id="invalid",
        )


def test_round_rejects_invalid_season_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="season deve ser Season",
    ):
        make_round(
            season,
            season_value="invalid",
        )


def test_round_rejects_invalid_name_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="name deve ser Name",
    ):
        make_round(
            season,
            name="Rodada 1",
        )


def test_round_rejects_invalid_round_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="round_type deve ser RoundType",
    ):
        make_round(
            season,
            round_type="regular",
        )


# ============================================================
# Fase e hierarquia
# ============================================================


def test_round_may_belong_directly_to_season(
    season,
) -> None:
    round_ = make_round(
        season,
        round_number=RoundNumber(1),
    )

    assert round_.stage is None
    assert round_.stage_id is None


def test_round_accepts_stage_from_same_season(
    season,
    stage,
) -> None:
    round_ = make_round(
        season,
        stage=stage,
        round_type=RoundType.GROUP,
    )

    assert round_.stage == stage
    assert round_.stage_id == stage.id


def test_round_rejects_invalid_stage_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="stage deve ser Stage ou None",
    ):
        make_round(
            season,
            stage="invalid",
        )


def test_round_rejects_stage_from_another_season(
    stage,
) -> None:
    other_season = make_other_season()

    with pytest.raises(
        CompetitionHierarchyError,
        match=(
            "A fase da rodada deve pertencer "
            "à mesma temporada"
        ),
    ):
        make_round(
            other_season,
            stage=stage,
            round_type=RoundType.KNOCKOUT,
        )


def test_round_assigns_stage_immutably(
    season,
    stage,
) -> None:
    round_ = make_round(season)

    updated = round_.assign_stage(stage)

    assert updated is not round_
    assert updated == round_
    assert updated.stage == stage
    assert updated.stage_id == stage.id
    assert round_.stage is None


def test_round_assign_stage_rejects_invalid_type(
    season,
) -> None:
    round_ = make_round(season)

    with pytest.raises(
        TypeError,
        match="stage deve ser Stage",
    ):
        round_.assign_stage("invalid")


def test_round_assign_stage_reuses_hierarchy_validation(
    season,
) -> None:
    round_ = make_round(season)
    other_season = make_other_season()
    other_stage = make_stage_for_season(
        other_season
    )

    with pytest.raises(
        CompetitionHierarchyError
    ):
        round_.assign_stage(other_stage)


def test_round_clears_stage_immutably(
    season,
    stage,
) -> None:
    round_ = make_round(
        season,
        stage=stage,
    )

    updated = round_.clear_stage()

    assert updated is not round_
    assert updated == round_
    assert updated.stage is None
    assert updated.stage_id is None
    assert round_.stage == stage


def test_round_clear_stage_keeps_none(
    season,
) -> None:
    round_ = make_round(season)

    updated = round_.clear_stage()

    assert updated is not round_
    assert updated.stage is None
    assert round_.stage is None


# ============================================================
# Número e sequência
# ============================================================


def test_round_accepts_round_number(
    season,
) -> None:
    round_ = make_round(
        season,
        round_number=RoundNumber(1),
    )

    assert round_.round_number == RoundNumber(1)


def test_round_rejects_invalid_round_number_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "round_number deve ser RoundNumber ou None"
        ),
    ):
        make_round(
            season,
            round_number=1,
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
def test_round_rejects_invalid_sequence_type(
    season,
    invalid_sequence: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="sequence deve ser int ou None",
    ):
        make_round(
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
def test_round_rejects_non_positive_sequence(
    season,
    invalid_sequence: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "sequence deve ser maior ou igual a 1"
        ),
    ):
        make_round(
            season,
            sequence=invalid_sequence,
        )


def test_round_accepts_positive_sequence(
    season,
) -> None:
    round_ = make_round(
        season,
        sequence=1,
    )

    assert round_.sequence == 1


def test_round_reorders_immutably(
    season,
) -> None:
    round_ = make_round(
        season,
        sequence=1,
    )

    updated = round_.reorder(2)

    assert updated is not round_
    assert updated == round_
    assert updated.sequence == 2
    assert round_.sequence == 1


def test_round_reorder_accepts_none(
    season,
) -> None:
    round_ = make_round(
        season,
        sequence=1,
    )

    updated = round_.reorder(None)

    assert updated.sequence is None
    assert round_.sequence == 1


def test_round_reorder_reuses_constructor_validation(
    season,
) -> None:
    round_ = make_round(season)

    with pytest.raises(
        ValueError,
        match=(
            "sequence deve ser maior ou igual a 1"
        ),
    ):
        round_.reorder(0)


def test_round_renumbers_immutably(
    season,
) -> None:
    round_ = make_round(
        season,
        round_number=RoundNumber(1),
    )

    updated = round_.renumber(
        RoundNumber(2)
    )

    assert updated is not round_
    assert updated == round_
    assert updated.round_number == RoundNumber(2)
    assert round_.round_number == RoundNumber(1)


def test_round_renumber_accepts_none(
    season,
) -> None:
    round_ = make_round(
        season,
        round_number=RoundNumber(1),
    )

    updated = round_.renumber(None)

    assert updated.round_number is None
    assert round_.round_number == RoundNumber(1)


def test_round_renumber_reuses_constructor_validation(
    season,
) -> None:
    round_ = make_round(season)

    with pytest.raises(
        TypeError,
        match=(
            "round_number deve ser RoundNumber ou None"
        ),
    ):
        round_.renumber(1)


# ============================================================
# Período
# ============================================================


@pytest.mark.parametrize(
    "invalid_start_date",
    [
        "2026-01-01",
        20260101,
        True,
        object(),
    ],
)
def test_round_rejects_invalid_start_date_type(
    season,
    invalid_start_date: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "start_date deve ser DomainDate ou None"
        ),
    ):
        make_round(
            season,
            start_date=invalid_start_date,
        )


@pytest.mark.parametrize(
    "invalid_end_date",
    [
        "2026-01-02",
        20260102,
        True,
        object(),
    ],
)
def test_round_rejects_invalid_end_date_type(
    season,
    invalid_end_date: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "end_date deve ser DomainDate ou None"
        ),
    ):
        make_round(
            season,
            end_date=invalid_end_date,
        )


def test_round_rejects_inverted_period(
    season,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "start_date deve ser anterior ou igual "
            "a end_date"
        ),
    ):
        make_round(
            season,
            start_date=DomainDate("2026-01-02"),
            end_date=DomainDate("2026-01-01"),
        )


def test_round_accepts_equal_start_and_end_dates(
    season,
) -> None:
    date = DomainDate("2026-01-01")

    round_ = make_round(
        season,
        start_date=date,
        end_date=date,
    )

    assert round_.start_date == date
    assert round_.end_date == date


def test_round_accepts_only_start_date(
    season,
) -> None:
    round_ = make_round(
        season,
        start_date=DomainDate("2026-01-01"),
    )

    assert round_.start_date == DomainDate(
        "2026-01-01"
    )
    assert round_.end_date is None


def test_round_accepts_only_end_date(
    season,
) -> None:
    round_ = make_round(
        season,
        end_date=DomainDate("2026-01-02"),
    )

    assert round_.start_date is None
    assert round_.end_date == DomainDate(
        "2026-01-02"
    )


# ============================================================
# Aliases e flags
# ============================================================


def test_round_rejects_invalid_aliases_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="aliases deve ser CompetitionAliases",
    ):
        make_round(
            season,
            aliases=(AliasValue("R1"),),
        )


@pytest.mark.parametrize(
    "invalid_is_current",
    [
        1,
        0,
        "false",
        None,
    ],
)
def test_round_rejects_invalid_is_current_type(
    season,
    invalid_is_current: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="is_current deve ser bool",
    ):
        make_round(
            season,
            is_current=invalid_is_current,
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
def test_round_rejects_invalid_is_active_type(
    season,
    invalid_is_active: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="is_active deve ser bool",
    ):
        make_round(
            season,
            is_active=invalid_is_active,
        )


def test_round_adds_alias_immutably(
    season,
) -> None:
    round_ = make_round(season)
    alias = AliasValue("R1")

    updated = round_.add_alias(alias)

    assert updated is not round_
    assert updated == round_
    assert alias in updated.aliases
    assert alias not in round_.aliases


def test_round_removes_alias_immutably(
    season,
) -> None:
    alias = AliasValue("R1")

    round_ = make_round(
        season,
        aliases=CompetitionAliases((alias,)),
    )

    updated = round_.remove_alias(alias)

    assert updated is not round_
    assert updated == round_
    assert alias not in updated.aliases
    assert alias in round_.aliases


# ============================================================
# Estado atual e atividade
# ============================================================


def test_round_can_be_marked_as_current(
    season,
) -> None:
    round_ = make_round(season)

    updated = round_.mark_current()

    assert updated is not round_
    assert updated == round_
    assert updated.is_current is True
    assert round_.is_current is False


def test_round_can_clear_current_flag(
    season,
) -> None:
    round_ = make_round(
        season,
        is_current=True,
    )

    updated = round_.clear_current()

    assert updated is not round_
    assert updated == round_
    assert updated.is_current is False
    assert round_.is_current is True


def test_round_deactivate_clears_current_flag(
    season,
) -> None:
    round_ = make_round(
        season,
        is_current=True,
        is_active=True,
    )

    updated = round_.deactivate()

    assert updated is not round_
    assert updated == round_
    assert updated.is_active is False
    assert updated.is_current is False
    assert round_.is_active is True
    assert round_.is_current is True


def test_round_can_be_activated(
    season,
) -> None:
    round_ = make_round(
        season,
        is_active=False,
    )

    updated = round_.activate()

    assert updated is not round_
    assert updated == round_
    assert updated.is_active is True
    assert round_.is_active is False


# ============================================================
# Identidade
# ============================================================


def test_round_is_compared_by_identity(
    season,
) -> None:
    round_ = make_round(season)

    updated = round_.reorder(1)

    assert updated == round_
    assert hash(updated) == hash(round_)


def test_rounds_with_different_ids_are_not_equal(
    season,
) -> None:
    first = make_round(season)
    second = make_round(season)

    assert first != second


def test_round_equality_returns_not_equal_for_other_type(
    season,
) -> None:
    round_ = make_round(season)

    assert round_ != object()


def test_round_hash_is_based_on_id(
    season,
) -> None:
    round_ = make_round(season)

    assert hash(round_) == hash(round_.id)


# ============================================================
# Imutabilidade
# ============================================================


def test_round_is_immutable(
    season,
) -> None:
    round_ = make_round(season)

    with pytest.raises(FrozenInstanceError):
        round_.sequence = 10