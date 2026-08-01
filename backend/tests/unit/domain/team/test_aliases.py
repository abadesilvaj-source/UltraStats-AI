"""Testes da coleção imutável TeamAliases."""

from dataclasses import FrozenInstanceError

import pytest

from ultrastats_ai.domain.shared import AliasValue
from ultrastats_ai.domain.team import (
    DuplicateTeamAliasError,
    TeamAliasNotFoundError,
    TeamAliases,
)


def test_team_aliases_is_empty_by_default() -> None:
    aliases = TeamAliases()

    assert aliases.values == ()
    assert len(aliases) == 0
    assert not aliases
    assert list(aliases) == []


def test_team_aliases_empty_factory() -> None:
    aliases = TeamAliases.empty()

    assert aliases == TeamAliases()
    assert len(aliases) == 0


def test_team_aliases_accepts_tuple() -> None:
    first = AliasValue("São Paulo FC")
    second = AliasValue("Tricolor Paulista")

    aliases = TeamAliases(
        (
            first,
            second,
        )
    )

    assert aliases.values == (
        first,
        second,
    )
    assert len(aliases) == 2
    assert aliases


def test_team_aliases_rejects_non_tuple_values() -> None:
    with pytest.raises(
        TypeError,
        match="values deve ser tuple",
    ):
        TeamAliases(
            [AliasValue("São Paulo FC")]  # type: ignore[arg-type]
        )


def test_team_aliases_rejects_invalid_item_type() -> None:
    with pytest.raises(
        TypeError,
        match="Todos os aliases devem ser AliasValue",
    ):
        TeamAliases(
            ("São Paulo FC",)  # type: ignore[arg-type]
        )


def test_team_aliases_rejects_exact_duplicate() -> None:
    with pytest.raises(DuplicateTeamAliasError):
        TeamAliases(
            (
                AliasValue("São Paulo FC"),
                AliasValue("São Paulo FC"),
            )
        )


def test_team_aliases_rejects_normalized_duplicate() -> None:
    with pytest.raises(DuplicateTeamAliasError):
        TeamAliases(
            (
                AliasValue("São Paulo FC"),
                AliasValue("  SÃO   PAULO fc  "),
            )
        )


def test_team_aliases_from_iterable() -> None:
    source = [
        AliasValue("São Paulo FC"),
        AliasValue("Tricolor Paulista"),
    ]

    aliases = TeamAliases.from_iterable(source)

    assert aliases.values == tuple(source)


def test_team_aliases_from_generator() -> None:
    source = (
        AliasValue(value)
        for value in (
            "São Paulo FC",
            "Tricolor Paulista",
        )
    )

    aliases = TeamAliases.from_iterable(source)

    assert len(aliases) == 2


@pytest.mark.parametrize(
    "invalid_value",
    [
        "São Paulo FC",
        "São Paulo FC".encode("utf-8"),
        123,
        None,
    ],
)

def test_team_aliases_from_iterable_rejects_invalid_input(
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="aliases deve ser um iterável",
    ):
        TeamAliases.from_iterable(
            invalid_value  # type: ignore[arg-type]
        )


def test_team_aliases_adds_alias_immutably() -> None:
    aliases = TeamAliases.empty()
    alias = AliasValue("São Paulo FC")

    updated = aliases.add(alias)

    assert updated is not aliases
    assert alias in updated
    assert alias not in aliases
    assert len(updated) == 1


def test_team_aliases_add_rejects_invalid_type() -> None:
    aliases = TeamAliases.empty()

    with pytest.raises(
        TypeError,
        match="alias deve ser AliasValue",
    ):
        aliases.add(
            "São Paulo FC"  # type: ignore[arg-type]
        )


def test_team_aliases_add_rejects_duplicate() -> None:
    aliases = TeamAliases(
        (
            AliasValue("São Paulo FC"),
        )
    )

    with pytest.raises(DuplicateTeamAliasError):
        aliases.add(
            AliasValue("  SÃO PAULO FC ")
        )


def test_team_aliases_removes_alias_immutably() -> None:
    first = AliasValue("São Paulo FC")
    second = AliasValue("Tricolor Paulista")

    aliases = TeamAliases(
        (
            first,
            second,
        )
    )

    updated = aliases.remove(
        AliasValue("  SÃO PAULO fc ")
    )

    assert updated is not aliases
    assert first not in updated
    assert second in updated
    assert first in aliases


def test_team_aliases_remove_rejects_invalid_type() -> None:
    aliases = TeamAliases.empty()

    with pytest.raises(
        TypeError,
        match="alias deve ser AliasValue",
    ):
        aliases.remove(
            "São Paulo FC"  # type: ignore[arg-type]
        )


def test_team_aliases_remove_rejects_missing_alias() -> None:
    aliases = TeamAliases(
        (
            AliasValue("São Paulo FC"),
        )
    )

    with pytest.raises(TeamAliasNotFoundError):
        aliases.remove(
            AliasValue("Palmeiras")
        )


@pytest.mark.parametrize(
    "search_value",
    [
        "São Paulo FC",
        "são paulo fc",
        " SÃO   PAULO FC ",
    ],
)
def test_team_aliases_contains_normalized_text(
    search_value: str,
) -> None:
    aliases = TeamAliases(
        (
            AliasValue("São Paulo FC"),
        )
    )

    assert aliases.contains_text(search_value)


def test_team_aliases_does_not_contain_unknown_text() -> None:
    aliases = TeamAliases(
        (
            AliasValue("São Paulo FC"),
        )
    )

    assert not aliases.contains_text("Palmeiras")


def test_team_aliases_contains_text_rejects_invalid_type() -> None:
    aliases = TeamAliases.empty()

    with pytest.raises(
        TypeError,
        match="value deve ser str",
    ):
        aliases.contains_text(
            123  # type: ignore[arg-type]
        )


def test_team_aliases_contains_alias_value() -> None:
    alias = AliasValue("São Paulo FC")
    aliases = TeamAliases((alias,))

    assert alias in aliases


def test_team_aliases_contains_normalized_alias_value() -> None:
    aliases = TeamAliases(
        (
            AliasValue("São Paulo FC"),
        )
    )

    assert AliasValue(" SÃO PAULO FC ") in aliases


def test_team_aliases_does_not_contain_invalid_object() -> None:
    aliases = TeamAliases.empty()

    assert "São Paulo FC" not in aliases
    assert object() not in aliases


def test_team_aliases_is_iterable() -> None:
    first = AliasValue("São Paulo FC")
    second = AliasValue("Tricolor Paulista")

    aliases = TeamAliases(
        (
            first,
            second,
        )
    )

    assert list(aliases) == [
        first,
        second,
    ]


def test_team_aliases_supports_index_access() -> None:
    first = AliasValue("São Paulo FC")
    second = AliasValue("Tricolor Paulista")

    aliases = TeamAliases(
        (
            first,
            second,
        )
    )

    assert aliases[0] == first
    assert aliases[1] == second


def test_team_aliases_preserves_order() -> None:
    aliases = (
        TeamAliases.empty()
        .add(AliasValue("Primeiro"))
        .add(AliasValue("Segundo"))
        .add(AliasValue("Terceiro"))
    )

    assert [
        alias.value
        for alias in aliases
    ] == [
        "Primeiro",
        "Segundo",
        "Terceiro",
    ]


def test_team_aliases_equality_uses_values() -> None:
    first = TeamAliases(
        (
            AliasValue("São Paulo FC"),
        )
    )

    second = TeamAliases(
        (
            AliasValue("São Paulo FC"),
        )
    )

    assert first == second
    assert hash(first) == hash(second)


def test_team_aliases_is_immutable() -> None:
    aliases = TeamAliases.empty()

    with pytest.raises(FrozenInstanceError):
        aliases.values = (
            AliasValue("São Paulo FC"),
        )