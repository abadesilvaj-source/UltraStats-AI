"""Testes do Aggregate Root conceitual Season."""

from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from ultrastats_ai.domain.competition import (
    CompetitionAliases,
    InvalidSeasonTransitionError,
    NameAliasConflictError,
    Season,
)
from ultrastats_ai.domain.shared import (
    AliasValue,
    DomainDate,
    Name,
    SeasonId,
    SeasonStatus,
)


_UNSET = object()


def make_season(
    competition,
    *,
    id: Any = _UNSET,
    name: Any = _UNSET,
    status: Any = SeasonStatus.PLANNED,
    start_date: Any = _UNSET,
    end_date: Any = _UNSET,
    aliases: Any = _UNSET,
    is_current: Any = False,
    is_active: Any = True,
    competition_value: Any = _UNSET,
) -> Season:
    """Cria uma temporada válida com campos sobrescrevíveis."""

    return Season(
        id=(
            SeasonId.new()
            if id is _UNSET
            else id
        ),
        competition=(
            competition
            if competition_value is _UNSET
            else competition_value
        ),
        name=(
            Name("2026")
            if name is _UNSET
            else name
        ),
        status=status,
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


# ============================================================
# Criação
# ============================================================


def test_season_is_created_with_required_fields(
    competition,
) -> None:
    season = make_season(competition)

    assert isinstance(season.id, SeasonId)
    assert season.competition == competition
    assert season.competition_id == competition.id
    assert season.name == Name("2026")
    assert season.status is SeasonStatus.PLANNED
    assert season.start_date is None
    assert season.end_date is None
    assert season.aliases == CompetitionAliases.empty()
    assert season.is_current is False
    assert season.is_active is True


def test_season_accepts_optional_fields(
    competition,
) -> None:
    aliases = CompetitionAliases(
        (
            AliasValue("Temporada 2026"),
            AliasValue("Edição 2026"),
        )
    )

    season = make_season(
        competition,
        status=SeasonStatus.ACTIVE,
        start_date=DomainDate("2026-01-01"),
        end_date=DomainDate("2026-12-31"),
        aliases=aliases,
        is_current=True,
        is_active=False,
    )

    assert season.status is SeasonStatus.ACTIVE
    assert season.start_date == DomainDate("2026-01-01")
    assert season.end_date == DomainDate("2026-12-31")
    assert season.aliases == aliases
    assert season.is_current is True
    assert season.is_active is False


# ============================================================
# Validações do construtor
# ============================================================


def test_season_rejects_invalid_id_type(
    competition,
) -> None:
    with pytest.raises(
        TypeError,
        match="id deve ser SeasonId",
    ):
        make_season(
            competition,
            id="invalid",
        )


def test_season_rejects_invalid_competition_type(
    competition,
) -> None:
    with pytest.raises(
        TypeError,
        match="competition deve ser Competition",
    ):
        make_season(
            competition,
            competition_value="invalid",
        )


def test_season_rejects_invalid_name_type(
    competition,
) -> None:
    with pytest.raises(
        TypeError,
        match="name deve ser Name",
    ):
        make_season(
            competition,
            name="2026",
        )


def test_season_rejects_invalid_status_type(
    competition,
) -> None:
    with pytest.raises(
        TypeError,
        match="status deve ser SeasonStatus",
    ):
        make_season(
            competition,
            status="planned",
        )


@pytest.mark.parametrize(
    "invalid_start_date",
    [
        "2026-01-01",
        20260101,
        True,
        object(),
    ],
)
def test_season_rejects_invalid_start_date_type(
    competition,
    invalid_start_date: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "start_date deve ser DomainDate ou None"
        ),
    ):
        make_season(
            competition,
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
def test_season_rejects_invalid_end_date_type(
    competition,
    invalid_end_date: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "end_date deve ser DomainDate ou None"
        ),
    ):
        make_season(
            competition,
            end_date=invalid_end_date,
        )


def test_season_rejects_inverted_period(
    competition,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "start_date deve ser anterior ou igual "
            "a end_date"
        ),
    ):
        make_season(
            competition,
            start_date=DomainDate("2026-12-31"),
            end_date=DomainDate("2026-01-01"),
        )


def test_season_accepts_equal_start_and_end_dates(
    competition,
) -> None:
    date = DomainDate("2026-01-01")

    season = make_season(
        competition,
        start_date=date,
        end_date=date,
    )

    assert season.start_date == date
    assert season.end_date == date


def test_season_rejects_invalid_aliases_type(
    competition,
) -> None:
    with pytest.raises(
        TypeError,
        match="aliases deve ser CompetitionAliases",
    ):
        make_season(
            competition,
            aliases=(AliasValue("2026"),),
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
def test_season_rejects_invalid_is_current_type(
    competition,
    invalid_is_current: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="is_current deve ser bool",
    ):
        make_season(
            competition,
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
def test_season_rejects_invalid_is_active_type(
    competition,
    invalid_is_active: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="is_active deve ser bool",
    ):
        make_season(
            competition,
            is_active=invalid_is_active,
        )


@pytest.mark.parametrize(
    "terminal_status",
    [
        SeasonStatus.COMPLETED,
        SeasonStatus.CANCELLED,
    ],
)
def test_terminal_season_cannot_be_current(
    competition,
    terminal_status: SeasonStatus,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Temporada concluída ou cancelada não "
            "pode ser atual"
        ),
    ):
        make_season(
            competition,
            status=terminal_status,
            is_current=True,
        )


# ============================================================
# Nome e aliases
# ============================================================


def test_season_rejects_name_repeated_as_alias(
    competition,
) -> None:
    aliases = CompetitionAliases(
        (
            AliasValue("2026"),
        )
    )

    with pytest.raises(
        NameAliasConflictError,
        match=(
            "O nome da temporada não pode ser "
            "repetido como alias"
        ),
    ):
        make_season(
            competition,
            aliases=aliases,
        )


def test_season_detects_alias_conflict_case_insensitively(
    competition,
) -> None:
    aliases = CompetitionAliases(
        (
            AliasValue("TEMPORADA 2026"),
        )
    )

    with pytest.raises(NameAliasConflictError):
        make_season(
            competition,
            name=Name("Temporada 2026"),
            aliases=aliases,
        )


def test_season_detects_alias_conflict_after_space_normalization(
    competition,
) -> None:
    aliases = CompetitionAliases(
        (
            AliasValue("  Temporada   2026  "),
        )
    )

    with pytest.raises(NameAliasConflictError):
        make_season(
            competition,
            name=Name("Temporada 2026"),
            aliases=aliases,
        )


def test_season_accepts_distinct_alias(
    competition,
) -> None:
    alias = AliasValue("Edição atual")

    season = make_season(
        competition,
        aliases=CompetitionAliases((alias,))
    )

    assert alias in season.aliases


def test_season_adds_alias_immutably(
    season,
) -> None:
    alias = AliasValue("Temporada atual")

    updated = season.add_alias(alias)

    assert updated is not season
    assert updated == season
    assert alias in updated.aliases
    assert alias not in season.aliases


def test_season_removes_alias_immutably(
    competition,
) -> None:
    alias = AliasValue("Temporada atual")

    season = make_season(
        competition,
        aliases=CompetitionAliases((alias,))
    )

    updated = season.remove_alias(alias)

    assert updated is not season
    assert updated == season
    assert alias not in updated.aliases
    assert alias in season.aliases


# ============================================================
# Transições de status
# ============================================================


def test_season_transition_rejects_invalid_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="status deve ser SeasonStatus",
    ):
        season.transition_to("active")


def test_season_transition_to_same_status_returns_self(
    season,
) -> None:
    result = season.transition_to(
        SeasonStatus.PLANNED
    )

    assert result is season


def test_planned_season_can_become_active(
    season,
) -> None:
    updated = season.transition_to(
        SeasonStatus.ACTIVE
    )

    assert updated is not season
    assert updated.status is SeasonStatus.ACTIVE
    assert season.status is SeasonStatus.PLANNED


def test_planned_season_can_be_cancelled(
    season,
) -> None:
    updated = season.transition_to(
        SeasonStatus.CANCELLED
    )

    assert updated.status is SeasonStatus.CANCELLED
    assert updated.is_current is False


def test_active_season_can_be_suspended(
    season,
) -> None:
    active = season.transition_to(
        SeasonStatus.ACTIVE
    )

    suspended = active.transition_to(
        SeasonStatus.SUSPENDED
    )

    assert suspended.status is SeasonStatus.SUSPENDED


def test_suspended_season_can_be_reactivated(
    season,
) -> None:
    suspended = (
        season
        .transition_to(SeasonStatus.ACTIVE)
        .transition_to(SeasonStatus.SUSPENDED)
    )

    active = suspended.transition_to(
        SeasonStatus.ACTIVE
    )

    assert active.status is SeasonStatus.ACTIVE


def test_active_season_can_be_completed(
    season,
) -> None:
    completed = (
        season
        .transition_to(SeasonStatus.ACTIVE)
        .transition_to(SeasonStatus.COMPLETED)
    )

    assert completed.status is SeasonStatus.COMPLETED
    assert completed.is_current is False


def test_current_season_loses_current_flag_when_completed(
    competition,
) -> None:
    active = make_season(
        competition,
        status=SeasonStatus.ACTIVE,
        is_current=True,
    )

    completed = active.transition_to(
        SeasonStatus.COMPLETED
    )

    assert completed.status is SeasonStatus.COMPLETED
    assert completed.is_current is False


def test_current_season_loses_current_flag_when_cancelled(
    competition,
) -> None:
    active = make_season(
        competition,
        status=SeasonStatus.ACTIVE,
        is_current=True,
    )

    cancelled = active.transition_to(
        SeasonStatus.CANCELLED
    )

    assert cancelled.status is SeasonStatus.CANCELLED
    assert cancelled.is_current is False


def test_non_terminal_transition_preserves_current_flag(
    competition,
) -> None:
    active = make_season(
        competition,
        status=SeasonStatus.ACTIVE,
        is_current=True,
    )

    suspended = active.transition_to(
        SeasonStatus.SUSPENDED
    )

    assert suspended.status is SeasonStatus.SUSPENDED
    assert suspended.is_current is True


@pytest.mark.parametrize(
    "invalid_target",
    [
        SeasonStatus.SUSPENDED,
        SeasonStatus.COMPLETED,
    ],
)
def test_planned_season_rejects_invalid_transition(
    season,
    invalid_target: SeasonStatus,
) -> None:
    with pytest.raises(
        InvalidSeasonTransitionError,
        match="Transição inválida",
    ):
        season.transition_to(invalid_target)


@pytest.mark.parametrize(
    "terminal_status",
    [
        SeasonStatus.COMPLETED,
        SeasonStatus.CANCELLED,
    ],
)
def test_terminal_season_rejects_new_transition(
    competition,
    terminal_status: SeasonStatus,
) -> None:
    terminal = make_season(
        competition,
        status=terminal_status,
    )

    with pytest.raises(
        InvalidSeasonTransitionError,
        match="Transição inválida",
    ):
        terminal.transition_to(
            SeasonStatus.ACTIVE
        )


# ============================================================
# Alterações imutáveis
# ============================================================


def test_season_rename_returns_new_instance(
    season,
) -> None:
    new_name = Name("2027")

    updated = season.rename(new_name)

    assert updated is not season
    assert updated == season
    assert updated.name == new_name
    assert season.name == Name("2026")


def test_season_rename_rejects_invalid_type(
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="name deve ser Name",
    ):
        season.rename("2027")


def test_season_accepts_valid_period(
    season,
) -> None:
    updated = season.change_period(
        start_date=DomainDate("2026-01-01"),
        end_date=DomainDate("2026-12-31"),
    )

    assert updated is not season
    assert updated.start_date == DomainDate(
        "2026-01-01"
    )
    assert updated.end_date == DomainDate(
        "2026-12-31"
    )
    assert season.start_date is None
    assert season.end_date is None


def test_season_change_period_accepts_open_start(
    season,
) -> None:
    updated = season.change_period(
        start_date=None,
        end_date=DomainDate("2026-12-31"),
    )

    assert updated.start_date is None
    assert updated.end_date == DomainDate(
        "2026-12-31"
    )


def test_season_change_period_accepts_open_end(
    season,
) -> None:
    updated = season.change_period(
        start_date=DomainDate("2026-01-01"),
        end_date=None,
    )

    assert updated.start_date == DomainDate(
        "2026-01-01"
    )
    assert updated.end_date is None


def test_season_change_period_rejects_inverted_period(
    season,
) -> None:
    with pytest.raises(ValueError):
        season.change_period(
            start_date=DomainDate("2026-12-31"),
            end_date=DomainDate("2026-01-01"),
        )


# ============================================================
# Estado atual e atividade
# ============================================================


def test_season_can_be_marked_as_current(
    season,
) -> None:
    updated = season.mark_current()

    assert updated is not season
    assert updated.is_current is True
    assert season.is_current is False


def test_season_can_clear_current_flag(
    competition,
) -> None:
    season = make_season(
        competition,
        is_current=True,
    )

    updated = season.clear_current()

    assert updated is not season
    assert updated.is_current is False
    assert season.is_current is True


def test_season_can_be_deactivated(
    competition,
) -> None:
    season = make_season(
        competition,
        is_current=True,
        is_active=True,
    )

    updated = season.deactivate()

    assert updated is not season
    assert updated.is_active is False
    assert updated.is_current is False
    assert season.is_active is True
    assert season.is_current is True


def test_season_can_be_activated(
    competition,
) -> None:
    season = make_season(
        competition,
        is_active=False,
    )

    updated = season.activate()

    assert updated is not season
    assert updated.is_active is True
    assert season.is_active is False


# ============================================================
# Identidade
# ============================================================


def test_season_is_compared_by_identity(
    season,
) -> None:
    renamed = season.rename(Name("2027"))

    assert renamed == season
    assert hash(renamed) == hash(season)


def test_seasons_with_different_ids_are_not_equal(
    competition,
    season,
) -> None:
    other = make_season(competition)

    assert other != season


def test_season_equality_returns_not_equal_for_other_type(
    season,
) -> None:
    assert season != object()


def test_season_hash_is_based_on_id(
    season,
) -> None:
    assert hash(season) == hash(season.id)


# ============================================================
# Imutabilidade
# ============================================================


def test_season_is_immutable(
    season,
) -> None:
    with pytest.raises(FrozenInstanceError):
        season.name = Name("2027")