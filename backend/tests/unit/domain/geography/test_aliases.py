"""Testes da coleção Aliases."""

import pytest

from ultrastats_ai.domain.geography.aliases import Aliases
from ultrastats_ai.domain.geography.errors import (
    AliasNotFoundError,
    DuplicateAliasError,
)
from ultrastats_ai.domain.shared import AliasValue


def test_empty_creates_an_empty_collection() -> None:
    aliases = Aliases.empty()

    assert len(aliases) == 0
    assert aliases.as_tuple() == ()
    assert not aliases


def test_from_iterable_preserves_alias_order() -> None:
    first = AliasValue("Itaquerão")
    second = AliasValue("Arena Corinthians")

    aliases = Aliases.from_iterable(
        [
            first,
            second,
        ]
    )

    assert aliases.as_tuple() == (
        first,
        second,
    )


def test_add_returns_a_new_collection() -> None:
    original = Aliases.empty()
    alias = AliasValue("Itaquerão")

    updated = original.add(alias)

    assert original.as_tuple() == ()
    assert updated.as_tuple() == (alias,)
    assert updated is not original


def test_add_preserves_existing_aliases() -> None:
    first = AliasValue("Itaquerão")
    second = AliasValue("Arena Corinthians")

    original = Aliases.from_iterable([first])
    updated = original.add(second)

    assert original.as_tuple() == (first,)
    assert updated.as_tuple() == (
        first,
        second,
    )


def test_add_rejects_duplicate_alias() -> None:
    alias = AliasValue("Itaquerão")
    aliases = Aliases.from_iterable([alias])

    with pytest.raises(
        DuplicateAliasError,
        match="já existe",
    ):
        aliases.add(alias)


def test_constructor_rejects_duplicate_aliases() -> None:
    alias = AliasValue("Itaquerão")

    with pytest.raises(
        DuplicateAliasError,
        match="já existe",
    ):
        Aliases((alias, alias))


def test_alias_normalization_detects_semantic_duplicates() -> None:
    normalized = AliasValue("Arena Corinthians")
    equivalent = AliasValue("  Arena   Corinthians  ")

    with pytest.raises(DuplicateAliasError):
        Aliases.from_iterable(
            [
                normalized,
                equivalent,
            ]
        )


def test_discard_returns_collection_without_alias() -> None:
    first = AliasValue("Itaquerão")
    second = AliasValue("Arena Corinthians")

    original = Aliases.from_iterable(
        [
            first,
            second,
        ]
    )

    updated = original.discard(first)

    assert original.as_tuple() == (
        first,
        second,
    )
    assert updated.as_tuple() == (second,)


def test_discard_rejects_missing_alias() -> None:
    aliases = Aliases.empty()
    alias = AliasValue("Itaquerão")

    with pytest.raises(
        AliasNotFoundError,
        match="não existe",
    ):
        aliases.discard(alias)


def test_contains_returns_true_for_existing_alias() -> None:
    alias = AliasValue("Itaquerão")
    aliases = Aliases.from_iterable([alias])

    assert aliases.contains(alias)
    assert alias in aliases


def test_contains_returns_false_for_missing_alias() -> None:
    existing = AliasValue("Itaquerão")
    missing = AliasValue("Arena Corinthians")

    aliases = Aliases.from_iterable([existing])

    assert not aliases.contains(missing)
    assert missing not in aliases


def test_contains_returns_false_for_invalid_type() -> None:
    aliases = Aliases.empty()

    assert not aliases.contains("Itaquerão")  # type: ignore[arg-type]


def test_collection_is_iterable() -> None:
    first = AliasValue("Itaquerão")
    second = AliasValue("Arena Corinthians")

    aliases = Aliases.from_iterable(
        [
            first,
            second,
        ]
    )

    assert list(aliases) == [
        first,
        second,
    ]


def test_collection_length_matches_number_of_aliases() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("Itaquerão"),
            AliasValue("Arena Corinthians"),
        ]
    )

    assert len(aliases) == 2


def test_collection_is_truthy_when_not_empty() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("Itaquerão"),
        ]
    )

    assert aliases


@pytest.mark.parametrize(
    "invalid_value",
    [
        "Itaquerão",
        10,
        None,
        object(),
    ],
)
def test_constructor_rejects_non_alias_value_items(
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="AliasValue",
    ):
        Aliases((invalid_value,))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "invalid_value",
    [
        "Itaquerão",
        10,
        None,
        object(),
    ],
)
def test_add_rejects_non_alias_value(
    invalid_value: object,
) -> None:
    aliases = Aliases.empty()

    with pytest.raises(
        TypeError,
        match="AliasValue",
    ):
        aliases.add(invalid_value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "invalid_value",
    [
        "Itaquerão",
        10,
        None,
        object(),
    ],
)
def test_discard_rejects_non_alias_value(
    invalid_value: object,
) -> None:
    aliases = Aliases.empty()

    with pytest.raises(
        TypeError,
        match="AliasValue",
    ):
        aliases.discard(invalid_value)  # type: ignore[arg-type]