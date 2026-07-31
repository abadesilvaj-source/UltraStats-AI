"""Testes do tipo canônico AliasValue."""

import unicodedata

import pytest

from ultrastats_ai.domain.shared import AliasValue
from ultrastats_ai.domain.shared.aliases import (
    AliasValue as AliasesPackageAliasValue,
)
from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.text_value import TextValue


def test_alias_value_inherits_from_text_value() -> None:
    alias = AliasValue("São Paulo FC")

    assert isinstance(alias, TextValue)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("São Paulo FC", "São Paulo FC"),
        ("  São Paulo FC  ", "São Paulo FC"),
        ("São   Paulo   FC", "São Paulo FC"),
        ("Manchester\tUnited", "Manchester United"),
        ("Paris\nSaint-Germain", "Paris Saint-Germain"),
        ("PSG", "PSG"),
        ("1. FC Köln", "1. FC Köln"),
        ("Brighton & Hove Albion", "Brighton & Hove Albion"),
        ("Nott'm Forest", "Nott'm Forest"),
        ("PSG / Paris SG", "PSG / Paris SG"),
    ],
)
def test_alias_value_normalizes_whitespace_without_losing_human_spelling(
    value: str,
    expected: str,
) -> None:
    alias = AliasValue(value)

    assert alias.value == expected


def test_alias_value_normalizes_unicode_to_nfc() -> None:
    decomposed = unicodedata.normalize("NFD", "São Paulo")

    alias = AliasValue(decomposed)

    assert alias.value == "São Paulo"
    assert unicodedata.is_normalized("NFC", alias.value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "   ",
        "\t",
        "\n",
    ],
)
def test_alias_value_rejects_empty_values(value: str) -> None:
    with pytest.raises(
        DomainValidationError,
        match="AliasValue não pode ser vazio",
    ):
        AliasValue(value)


def test_alias_value_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="AliasValue deve ser criado a partir de uma string",
    ):
        AliasValue(123)  # type: ignore[arg-type]


def test_alias_value_rejects_value_longer_than_maximum() -> None:
    value = "a" * 129

    with pytest.raises(
        DomainValidationError,
        match=r"AliasValue deve possuir no máximo 128 caractere\(s\)",
    ):
        AliasValue(value)


def test_alias_value_accepts_value_at_maximum_length() -> None:
    value = "a" * 128

    alias = AliasValue(value)

    assert alias.value == value
    assert len(alias.value) == 128


def test_alias_value_equality_uses_normalized_value() -> None:
    first = AliasValue("  São   Paulo FC ")
    second = AliasValue("São Paulo FC")

    assert first == second
    assert hash(first) == hash(second)


def test_alias_value_preserves_case() -> None:
    uppercase = AliasValue("PSG")
    lowercase = AliasValue("psg")

    assert uppercase.value == "PSG"
    assert lowercase.value == "psg"
    assert uppercase != lowercase


def test_alias_value_preserves_accents() -> None:
    accented = AliasValue("São Paulo")
    unaccented = AliasValue("Sao Paulo")

    assert accented.value == "São Paulo"
    assert unaccented.value == "Sao Paulo"
    assert accented != unaccented


def test_alias_value_is_different_from_plain_text_value() -> None:
    alias = AliasValue("São Paulo FC")
    text = TextValue("São Paulo FC")

    assert alias != text


def test_alias_value_is_immutable() -> None:
    alias = AliasValue("São Paulo FC")

    with pytest.raises((AttributeError, TypeError)):
        alias.value = "SPFC"  # type: ignore[misc]


def test_alias_value_public_apis_export_same_class() -> None:
    assert AliasValue is AliasesPackageAliasValue