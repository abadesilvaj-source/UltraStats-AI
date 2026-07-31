"""Testes do Value Object DisplayName."""

import pytest

from ultrastats_ai.domain.shared.display_name import DisplayName
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_display_name_accepts_valid_name() -> None:
    name = DisplayName("Manchester United")

    assert name.value == "Manchester United"


def test_display_name_normalizes_whitespace() -> None:
    name = DisplayName("  Manchester    United  ")

    assert name.value == "Manchester United"


def test_display_name_accepts_single_alphanumeric_character() -> None:
    name = DisplayName("A")

    assert name.value == "A"


def test_display_name_accepts_unicode() -> None:
    name = DisplayName("São Paulo")

    assert name.value == "São Paulo"


def test_display_name_accepts_numbers() -> None:
    name = DisplayName("Formula 1")

    assert name.value == "Formula 1"


def test_display_name_rejects_empty_value() -> None:
    with pytest.raises(
        DomainValidationError,
        match="não pode ser vazio",
    ):
        DisplayName("   ")


def test_display_name_rejects_only_symbols() -> None:
    with pytest.raises(
        DomainValidationError,
        match="caractere alfanumérico",
    ):
        DisplayName("---")


def test_display_name_rejects_value_above_maximum_length() -> None:
    with pytest.raises(
        DomainValidationError,
        match="no máximo 100",
    ):
        DisplayName("A" * 101)


def test_display_name_string_representation_returns_value() -> None:
    name = DisplayName("Premier League")

    assert str(name) == "Premier League"