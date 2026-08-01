"""Testes da entidade canônica Competition."""

from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from ultrastats_ai.domain.competition import (
    Competition,
    CompetitionAliases,
    NameAliasConflictError,
)
from ultrastats_ai.domain.shared import (
    AliasValue,
    CompetitionCode,
    CompetitionId,
    CompetitionName,
    CompetitionType,
    CountryId,
)


_UNSET = object()


def make_competition(
    *,
    id: Any = _UNSET,
    code: Any = _UNSET,
    name: Any = _UNSET,
    competition_type: Any = _UNSET,
    country_id: Any = _UNSET,
    aliases: Any = _UNSET,
    is_active: Any = True,
) -> Competition:
    """Cria uma competição válida com campos sobrescrevíveis."""

    return Competition(
        id=(
            CompetitionId.new()
            if id is _UNSET
            else id
        ),
        code=(
            CompetitionCode("BRA-A")
            if code is _UNSET
            else code
        ),
        name=(
            CompetitionName(
                "Campeonato Brasileiro Série A"
            )
            if name is _UNSET
            else name
        ),
        competition_type=(
            CompetitionType.LEAGUE
            if competition_type is _UNSET
            else competition_type
        ),
        country_id=(
            None
            if country_id is _UNSET
            else country_id
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


def test_competition_is_created_with_required_fields() -> None:
    competition = make_competition()

    assert isinstance(competition.id, CompetitionId)
    assert competition.code == CompetitionCode("BRA-A")
    assert competition.name == CompetitionName(
        "Campeonato Brasileiro Série A"
    )
    assert (
        competition.competition_type
        is CompetitionType.LEAGUE
    )
    assert competition.country_id is None
    assert competition.aliases == CompetitionAliases.empty()
    assert competition.is_active is True


def test_competition_accepts_optional_fields() -> None:
    country_id = CountryId.new()

    aliases = CompetitionAliases(
        (
            AliasValue("Brasileirão"),
            AliasValue("Série A"),
        )
    )

    competition = make_competition(
        country_id=country_id,
        aliases=aliases,
        is_active=False,
    )

    assert competition.country_id == country_id
    assert competition.aliases == aliases
    assert competition.is_active is False


# ============================================================
# Validações do construtor
# ============================================================


def test_competition_rejects_invalid_id_type() -> None:
    with pytest.raises(
        TypeError,
        match="id deve ser CompetitionId",
    ):
        make_competition(id="invalid")


def test_competition_rejects_invalid_code_type() -> None:
    with pytest.raises(
        TypeError,
        match="code deve ser CompetitionCode",
    ):
        make_competition(code="BRA-A")


def test_competition_rejects_invalid_name_type() -> None:
    with pytest.raises(
        TypeError,
        match="name deve ser CompetitionName",
    ):
        make_competition(
            name="Campeonato Brasileiro Série A"
        )


def test_competition_rejects_invalid_competition_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "competition_type deve ser CompetitionType"
        ),
    ):
        make_competition(
            competition_type="league"
        )


@pytest.mark.parametrize(
    "invalid_country_id",
    [
        "BRA",
        1,
        True,
        object(),
    ],
)
def test_competition_rejects_invalid_country_id_type(
    invalid_country_id: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "country_id deve ser CountryId ou None"
        ),
    ):
        make_competition(
            country_id=invalid_country_id
        )


def test_competition_rejects_invalid_aliases_type() -> None:
    with pytest.raises(
        TypeError,
        match="aliases deve ser CompetitionAliases",
    ):
        make_competition(
            aliases=(AliasValue("Brasileirão"),)
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
def test_competition_rejects_invalid_is_active_type(
    invalid_is_active: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="is_active deve ser bool",
    ):
        make_competition(
            is_active=invalid_is_active
        )


# ============================================================
# Nome e aliases
# ============================================================


def test_competition_rejects_name_repeated_as_alias() -> None:
    aliases = CompetitionAliases(
        (
            AliasValue(
                "Campeonato Brasileiro Série A"
            ),
        )
    )

    with pytest.raises(
        NameAliasConflictError,
        match=(
            "O nome principal da competição não pode "
            "ser repetido como alias"
        ),
    ):
        make_competition(aliases=aliases)


def test_competition_detects_alias_conflict_case_insensitively(
) -> None:
    aliases = CompetitionAliases(
        (
            AliasValue(
                "CAMPEONATO BRASILEIRO SÉRIE A"
            ),
        )
    )

    with pytest.raises(NameAliasConflictError):
        make_competition(aliases=aliases)


def test_competition_detects_alias_conflict_after_space_normalization(
) -> None:
    aliases = CompetitionAliases(
        (
            AliasValue(
                "  Campeonato   Brasileiro Série A  "
            ),
        )
    )

    with pytest.raises(NameAliasConflictError):
        make_competition(aliases=aliases)


def test_competition_accepts_alias_different_from_name() -> None:
    alias = AliasValue("Brasileirão")

    competition = make_competition(
        aliases=CompetitionAliases((alias,))
    )

    assert alias in competition.aliases


def test_competition_accepts_multiple_distinct_aliases() -> None:
    aliases = CompetitionAliases(
        (
            AliasValue("Brasileirão"),
            AliasValue("Série A"),
        )
    )

    competition = make_competition(aliases=aliases)

    assert competition.aliases == aliases


def test_competition_adds_alias_immutably(
    competition,
) -> None:
    alias = AliasValue("Brasileirão")

    updated = competition.add_alias(alias)

    assert updated is not competition
    assert updated == competition
    assert alias in updated.aliases
    assert alias not in competition.aliases


def test_competition_removes_alias_immutably() -> None:
    alias = AliasValue("Brasileirão")

    competition = make_competition(
        aliases=CompetitionAliases((alias,))
    )

    updated = competition.remove_alias(alias)

    assert updated is not competition
    assert updated == competition
    assert alias not in updated.aliases
    assert alias in competition.aliases


# ============================================================
# Alterações imutáveis
# ============================================================


def test_competition_rename_returns_new_instance(
    competition,
) -> None:
    new_name = CompetitionName("Novo campeonato")

    updated = competition.rename(new_name)

    assert updated is not competition
    assert updated == competition
    assert updated.name == new_name
    assert competition.name != new_name


def test_competition_rename_rejects_invalid_type(
    competition,
) -> None:
    with pytest.raises(
        TypeError,
        match="name deve ser CompetitionName",
    ):
        competition.rename("Novo campeonato")


def test_competition_changes_code_immutably(
    competition,
) -> None:
    new_code = CompetitionCode("BRA-CUP")

    updated = competition.change_code(new_code)

    assert updated is not competition
    assert updated == competition
    assert updated.code == new_code
    assert competition.code == CompetitionCode("BRA-A")


def test_competition_change_code_rejects_invalid_type(
    competition,
) -> None:
    with pytest.raises(
        TypeError,
        match="code deve ser CompetitionCode",
    ):
        competition.change_code("BRA-CUP")


def test_competition_changes_type_immutably(
    competition,
) -> None:
    updated = competition.change_type(
        CompetitionType.CUP
    )

    assert updated is not competition
    assert updated == competition
    assert (
        updated.competition_type
        is CompetitionType.CUP
    )
    assert (
        competition.competition_type
        is CompetitionType.LEAGUE
    )


def test_competition_change_type_rejects_invalid_type(
    competition,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "competition_type deve ser CompetitionType"
        ),
    ):
        competition.change_type("cup")


def test_competition_assigns_country_immutably(
    competition,
) -> None:
    country_id = CountryId.new()

    updated = competition.assign_country(country_id)

    assert updated is not competition
    assert updated == competition
    assert updated.country_id == country_id
    assert competition.country_id is None


def test_competition_assign_country_rejects_invalid_type(
    competition,
) -> None:
    with pytest.raises(
        TypeError,
        match="country_id deve ser CountryId",
    ):
        competition.assign_country("BRA")


def test_competition_clears_country_immutably() -> None:
    country_id = CountryId.new()

    competition = make_competition(
        country_id=country_id
    )

    updated = competition.clear_country()

    assert updated is not competition
    assert updated == competition
    assert updated.country_id is None
    assert competition.country_id == country_id


def test_competition_clear_country_keeps_none(
    competition,
) -> None:
    updated = competition.clear_country()

    assert updated is not competition
    assert updated.country_id is None
    assert competition.country_id is None


# ============================================================
# Estado de atividade
# ============================================================


def test_competition_can_be_deactivated(
    competition,
) -> None:
    updated = competition.deactivate()

    assert updated is not competition
    assert updated == competition
    assert updated.is_active is False
    assert competition.is_active is True


def test_competition_can_be_activated() -> None:
    competition = make_competition(
        is_active=False
    )

    updated = competition.activate()

    assert updated is not competition
    assert updated == competition
    assert updated.is_active is True
    assert competition.is_active is False


# ============================================================
# Identidade
# ============================================================


def test_competition_is_compared_by_identity(
    competition,
) -> None:
    renamed = competition.rename(
        CompetitionName("Novo nome")
    )

    assert renamed == competition
    assert hash(renamed) == hash(competition)


def test_competitions_with_different_ids_are_not_equal(
    competition,
) -> None:
    other = make_competition()

    assert other != competition


def test_competition_equality_returns_not_equal_for_other_type(
    competition,
) -> None:
    assert competition != object()


def test_competition_hash_is_based_on_id(
    competition,
) -> None:
    assert hash(competition) == hash(competition.id)


# ============================================================
# Imutabilidade
# ============================================================


def test_competition_is_immutable(
    competition,
) -> None:
    with pytest.raises(FrozenInstanceError):
        competition.name = CompetitionName(
            "Nome alterado"
        )