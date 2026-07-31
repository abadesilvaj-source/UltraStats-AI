"""Testes da coleção CompetitionAliases."""

from dataclasses import FrozenInstanceError

import pytest

from ultrastats_ai.domain.competition import (
    AliasNotFoundError,
    CompetitionAliases,
    DuplicateAliasError,
)
from ultrastats_ai.domain.shared import AliasValue


def test_empty_creates_empty_collection() -> None:
    aliases = CompetitionAliases.empty()

    assert aliases.as_tuple() == ()
    assert len(aliases) == 0
    assert bool(aliases) is False


def test_default_constructor_creates_empty_collection() -> None:
    aliases = CompetitionAliases()

    assert aliases.as_tuple() == ()


def test_from_iterable_preserves_order() -> None:
    first = AliasValue("Brasileirão")
    second = AliasValue("Série A")

    aliases = CompetitionAliases.from_iterable(
        [first, second]
    )

    assert aliases.as_tuple() == (first, second)


def test_from_iterable_accepts_tuple() -> None:
    first = AliasValue("Brasileirão")
    second = AliasValue("Série A")

    aliases = CompetitionAliases.from_iterable(
        (first, second)
    )

    assert aliases.as_tuple() == (first, second)


def test_from_iterable_accepts_generator() -> None:
    values = (
        AliasValue(value)
        for value in ("Brasileirão", "Série A")
    )

    aliases = CompetitionAliases.from_iterable(values)

    assert len(aliases) == 2


@pytest.mark.parametrize(
    "invalid_value",
    [
        "Brasileirão",
        b"Brasileirao",
    ],
)
def test_from_iterable_rejects_text_and_bytes(
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="iterável de AliasValue",
    ):
        CompetitionAliases.from_iterable(invalid_value)


def test_constructor_rejects_non_alias_value() -> None:
    with pytest.raises(
        TypeError,
        match="AliasValue",
    ):
        CompetitionAliases(("Brasileirão",))


def test_constructor_rejects_duplicate_alias() -> None:
    alias = AliasValue("Brasileirão")

    with pytest.raises(DuplicateAliasError):
        CompetitionAliases((alias, alias))


def test_add_returns_new_collection() -> None:
    original = CompetitionAliases.empty()
    alias = AliasValue("Brasileirão")

    updated = original.add(alias)

    assert updated is not original
    assert len(original) == 0
    assert updated.as_tuple() == (alias,)


def test_add_preserves_existing_order() -> None:
    first = AliasValue("Brasileirão")
    second = AliasValue("Série A")

    original = CompetitionAliases((first,))
    updated = original.add(second)

    assert updated.as_tuple() == (first, second)


def test_add_rejects_invalid_type() -> None:
    aliases = CompetitionAliases.empty()

    with pytest.raises(
        TypeError,
        match="alias deve ser AliasValue",
    ):
        aliases.add("Brasileirão")


def test_add_rejects_duplicate_alias() -> None:
    alias = AliasValue("Brasileirão")
    aliases = CompetitionAliases((alias,))

    with pytest.raises(DuplicateAliasError):
        aliases.add(alias)


def test_discard_returns_new_collection() -> None:
    first = AliasValue("Brasileirão")
    second = AliasValue("Série A")
    original = CompetitionAliases((first, second))

    updated = original.discard(first)

    assert updated is not original
    assert original.as_tuple() == (first, second)
    assert updated.as_tuple() == (second,)


def test_discard_rejects_invalid_type() -> None:
    aliases = CompetitionAliases.empty()

    with pytest.raises(
        TypeError,
        match="alias deve ser AliasValue",
    ):
        aliases.discard("Brasileirão")


def test_discard_rejects_missing_alias() -> None:
    aliases = CompetitionAliases.empty()
    missing = AliasValue("Inexistente")

    with pytest.raises(AliasNotFoundError):
        aliases.discard(missing)


def test_contains_method_returns_true_for_existing_alias() -> None:
    alias = AliasValue("Brasileirão")
    aliases = CompetitionAliases((alias,))

    assert aliases.contains(alias) is True


def test_contains_method_returns_false_for_missing_alias() -> None:
    aliases = CompetitionAliases.empty()

    assert aliases.contains(
        AliasValue("Inexistente")
    ) is False


def test_contains_method_returns_false_for_invalid_type() -> None:
    aliases = CompetitionAliases.empty()

    assert aliases.contains("Brasileirão") is False


def test_contains_operator_is_supported() -> None:
    alias = AliasValue("Brasileirão")
    aliases = CompetitionAliases((alias,))

    assert alias in aliases


def test_iteration_preserves_order() -> None:
    first = AliasValue("Brasileirão")
    second = AliasValue("Série A")
    aliases = CompetitionAliases((first, second))

    assert list(aliases) == [first, second]


def test_len_returns_number_of_aliases() -> None:
    aliases = CompetitionAliases(
        (
            AliasValue("Brasileirão"),
            AliasValue("Série A"),
        )
    )

    assert len(aliases) == 2


def test_bool_returns_true_for_non_empty_collection() -> None:
    aliases = CompetitionAliases(
        (AliasValue("Brasileirão"),)
    )

    assert bool(aliases) is True


def test_collection_is_immutable() -> None:
    aliases = CompetitionAliases.empty()

    with pytest.raises(FrozenInstanceError):
        aliases._values = (AliasValue("Outro"),)