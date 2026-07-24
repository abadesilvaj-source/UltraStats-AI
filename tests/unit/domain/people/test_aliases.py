"""Testes da coleção PersonAliases."""

from dataclasses import FrozenInstanceError

import pytest

from ultrastats_ai.domain.people import (
    DuplicatePersonAliasError,
    PersonAliasNotFoundError,
    PersonAliases,
)
from ultrastats_ai.domain.shared import AliasValue


def test_person_aliases_is_created_empty() -> None:
    aliases = PersonAliases.empty()

    assert aliases.values == ()
    assert len(aliases) == 0
    assert bool(aliases) is False


def test_person_aliases_accepts_alias_values() -> None:
    first = AliasValue("Neymar")
    second = AliasValue("Neymar Jr.")

    aliases = PersonAliases(
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
    assert bool(aliases) is True


def test_person_aliases_rejects_non_tuple_values() -> None:
    with pytest.raises(
        TypeError,
        match="values deve ser tuple",
    ):
        PersonAliases(
            [AliasValue("Neymar")]  # type: ignore[arg-type]
        )


def test_person_aliases_rejects_invalid_item_type() -> None:
    with pytest.raises(
        TypeError,
        match="somente AliasValue",
    ):
        PersonAliases(
            ("Neymar",)  # type: ignore[arg-type]
        )


def test_person_aliases_rejects_exact_duplicate() -> None:
    with pytest.raises(
        DuplicatePersonAliasError,
        match="está duplicado",
    ):
        PersonAliases(
            (
                AliasValue("Neymar"),
                AliasValue("Neymar"),
            )
        )


def test_person_aliases_rejects_case_insensitive_duplicate() -> None:
    with pytest.raises(DuplicatePersonAliasError):
        PersonAliases(
            (
                AliasValue("Neymar"),
                AliasValue("NEYMAR"),
            )
        )


def test_person_aliases_rejects_space_normalized_duplicate() -> None:
    with pytest.raises(DuplicatePersonAliasError):
        PersonAliases(
            (
                AliasValue("Neymar Jr."),
                AliasValue("  Neymar   Jr.  "),
            )
        )


def test_person_aliases_adds_alias_immutably() -> None:
    aliases = PersonAliases.empty()
    alias = AliasValue("Neymar")

    updated = aliases.add(alias)

    assert updated is not aliases
    assert alias in updated
    assert alias not in aliases
    assert len(updated) == 1
    assert len(aliases) == 0


def test_person_aliases_add_preserves_existing_aliases() -> None:
    first = AliasValue("Neymar")
    second = AliasValue("Neymar Jr.")

    aliases = PersonAliases((first,))

    updated = aliases.add(second)

    assert updated.values == (
        first,
        second,
    )
    assert aliases.values == (first,)


def test_person_aliases_add_rejects_invalid_type() -> None:
    aliases = PersonAliases.empty()

    with pytest.raises(
        TypeError,
        match="alias deve ser AliasValue",
    ):
        aliases.add("Neymar")  # type: ignore[arg-type]


def test_person_aliases_add_rejects_duplicate() -> None:
    aliases = PersonAliases(
        (
            AliasValue("Neymar"),
        )
    )

    with pytest.raises(
        DuplicatePersonAliasError,
        match="já pertence",
    ):
        aliases.add(
            AliasValue("NEYMAR")
        )


def test_person_aliases_removes_alias_immutably() -> None:
    first = AliasValue("Neymar")
    second = AliasValue("Neymar Jr.")

    aliases = PersonAliases(
        (
            first,
            second,
        )
    )

    updated = aliases.remove(first)

    assert updated is not aliases
    assert first not in updated
    assert second in updated
    assert first in aliases
    assert len(updated) == 1
    assert len(aliases) == 2


def test_person_aliases_remove_is_case_insensitive() -> None:
    aliases = PersonAliases(
        (
            AliasValue("Neymar"),
        )
    )

    updated = aliases.remove(
        AliasValue("NEYMAR")
    )

    assert updated == PersonAliases.empty()


def test_person_aliases_remove_rejects_invalid_type() -> None:
    aliases = PersonAliases.empty()

    with pytest.raises(
        TypeError,
        match="alias deve ser AliasValue",
    ):
        aliases.remove("Neymar")  # type: ignore[arg-type]


def test_person_aliases_remove_rejects_unknown_alias() -> None:
    aliases = PersonAliases(
        (
            AliasValue("Neymar"),
        )
    )

    with pytest.raises(
        PersonAliasNotFoundError,
        match="não pertence",
    ):
        aliases.remove(
            AliasValue("Neymar Jr.")
        )


def test_person_aliases_contains_alias() -> None:
    aliases = PersonAliases(
        (
            AliasValue("Neymar"),
        )
    )

    assert AliasValue("Neymar") in aliases
    assert AliasValue("NEYMAR") in aliases
    assert AliasValue("Outro nome") not in aliases


def test_person_aliases_contains_returns_false_for_other_type() -> None:
    aliases = PersonAliases(
        (
            AliasValue("Neymar"),
        )
    )

    assert "Neymar" not in aliases
    assert object() not in aliases


def test_person_aliases_contains_text() -> None:
    aliases = PersonAliases(
        (
            AliasValue("Neymar Jr."),
        )
    )

    assert aliases.contains_text(
        "neymar jr."
    )
    assert aliases.contains_text(
        "  NEYMAR   JR. "
    )
    assert not aliases.contains_text(
        "Outro nome"
    )


def test_person_aliases_contains_text_rejects_invalid_type() -> None:
    aliases = PersonAliases.empty()

    with pytest.raises(
        TypeError,
        match="value deve ser str",
    ):
        aliases.contains_text(123)  # type: ignore[arg-type]


def test_person_aliases_is_iterable() -> None:
    first = AliasValue("Neymar")
    second = AliasValue("Neymar Jr.")

    aliases = PersonAliases(
        (
            first,
            second,
        )
    )

    assert tuple(iter(aliases)) == (
        first,
        second,
    )


def test_person_aliases_is_immutable() -> None:
    aliases = PersonAliases.empty()

    with pytest.raises(FrozenInstanceError):
        aliases.values = (
            AliasValue("Neymar"),
        )