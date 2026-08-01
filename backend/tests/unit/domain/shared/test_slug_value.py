"""Testes do tipo canônico SlugValue."""

import pytest

from ultrastats_ai.domain.shared import SlugValue
from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.slugs import (
    SlugValue as SlugsPackageSlugValue,
)
from ultrastats_ai.domain.shared.text_value import TextValue


def test_slug_value_inherits_from_text_value() -> None:
    slug = SlugValue("premier-league")

    assert isinstance(slug, TextValue)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("FIFA", "fifa"),
        ("UEFA Champions League", "uefa-champions-league"),
        (" São Paulo Futebol Clube ", "sao-paulo-futebol-clube"),
        (
            "Campeonato Brasileiro Série A",
            "campeonato-brasileiro-serie-a",
        ),
        ("Competition 2026", "competition-2026"),
        ("multiple   spaces", "multiple-spaces"),
    ],
)
def test_slug_value_normalizes_valid_values(
    value: str,
    expected: str,
) -> None:
    slug = SlugValue(value)

    assert slug.value == expected


@pytest.mark.parametrize(
    "value",
    [
        "-premier-league",
        "premier-league-",
        "premier--league",
        "premier_league",
        "premier/league",
        "premier@league",
        "competition.2026",
    ],
)
def test_slug_value_rejects_invalid_characters_and_structure(
    value: str,
) -> None:
    with pytest.raises(
        DomainValidationError,
        match="SlugValue aceita apenas letras minúsculas",
    ):
        SlugValue(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "   ",
    ],
)
def test_slug_value_rejects_empty_values(value: str) -> None:
    with pytest.raises(
        DomainValidationError,
        match="SlugValue não pode ser vazio",
    ):
        SlugValue(value)


def test_slug_value_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="SlugValue deve ser criado a partir de uma string",
    ):
        SlugValue(123)  # type: ignore[arg-type]


def test_slug_value_rejects_value_longer_than_maximum() -> None:
    value = "a" * 129

    with pytest.raises(
        DomainValidationError,
        match=r"SlugValue deve possuir no máximo 128 caractere\(s\)",
    ):
        SlugValue(value)


def test_slug_value_accepts_value_at_maximum_length() -> None:
    value = "a" * 128

    slug = SlugValue(value)

    assert slug.value == value
    assert len(slug.value) == 128


def test_slug_value_equality_uses_normalized_value() -> None:
    first = SlugValue("São Paulo")
    second = SlugValue("sao-paulo")

    assert first == second
    assert hash(first) == hash(second)


def test_slug_value_is_different_from_plain_text_value() -> None:
    slug = SlugValue("premier-league")
    text = TextValue("premier-league")

    assert slug != text


def test_slug_value_is_immutable() -> None:
    slug = SlugValue("premier-league")

    with pytest.raises((AttributeError, TypeError)):
        slug.value = "champions-league"  # type: ignore[misc]


def test_slug_value_public_apis_export_same_class() -> None:
    assert SlugValue is SlugsPackageSlugValue