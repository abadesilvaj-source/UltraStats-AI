"""Testes do Value Object ProperName."""

from dataclasses import FrozenInstanceError

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.proper_name import ProperName


def test_proper_name_accepts_valid_name() -> None:
    name = ProperName("Manchester United Football Club")

    assert name.value == "Manchester United Football Club"


def test_proper_name_normalizes_whitespace() -> None:
    name = ProperName("  Manchester   United  ")

    assert name.value == "Manchester United"


def test_proper_name_preserves_unicode_characters() -> None:
    name = ProperName("Associação Portuguesa de Desportos")

    assert name.value == "Associação Portuguesa de Desportos"


def test_proper_name_accepts_non_latin_characters() -> None:
    name = ProperName("浦和レッドダイヤモンズ")

    assert name.value == "浦和レッドダイヤモンズ"


def test_proper_name_accepts_numbers() -> None:
    name = ProperName("Schalke 04")

    assert name.value == "Schalke 04"


def test_proper_name_rejects_single_character() -> None:
    with pytest.raises(
        DomainValidationError,
        match="pelo menos 2",
    ):
        ProperName("A")


def test_proper_name_rejects_only_symbols() -> None:
    with pytest.raises(
        DomainValidationError,
        match="caractere alfanumérico",
    ):
        ProperName("--")


def test_proper_name_rejects_value_above_maximum_length() -> None:
    with pytest.raises(
        DomainValidationError,
        match="no máximo 150",
    ):
        ProperName("A" * 151)


def test_proper_name_is_immutable() -> None:
    name = ProperName("Premier League")

    with pytest.raises(FrozenInstanceError):
        name.value = "La Liga"  # type: ignore[misc]


def test_proper_name_string_representation_returns_value() -> None:
    name = ProperName("Premier League")

    assert str(name) == "Premier League"