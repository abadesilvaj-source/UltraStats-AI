"""Testes do Value Object ShortName."""

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.short_name import ShortName


def test_short_name_accepts_abbreviation() -> None:
    name = ShortName("UCL")

    assert name.value == "UCL"


def test_short_name_accepts_regular_short_name() -> None:
    name = ShortName("Man United")

    assert name.value == "Man United"


def test_short_name_accepts_single_character() -> None:
    name = ShortName("A")

    assert name.value == "A"


def test_short_name_does_not_force_uppercase() -> None:
    name = ShortName("Brasileirão")

    assert name.value == "Brasileirão"


def test_short_name_normalizes_whitespace() -> None:
    name = ShortName("  Man    United  ")

    assert name.value == "Man United"


def test_short_name_accepts_unicode() -> None:
    name = ShortName("São Paulo")

    assert name.value == "São Paulo"


def test_short_name_rejects_empty_value() -> None:
    with pytest.raises(
        DomainValidationError,
        match="não pode ser vazio",
    ):
        ShortName("   ")


def test_short_name_rejects_only_symbols() -> None:
    with pytest.raises(
        DomainValidationError,
        match="caractere alfanumérico",
    ):
        ShortName("--")


def test_short_name_accepts_exact_maximum_length() -> None:
    value = "A" * 30

    name = ShortName(value)

    assert name.value == value


def test_short_name_rejects_value_above_maximum_length() -> None:
    with pytest.raises(
        DomainValidationError,
        match="no máximo 30",
    ):
        ShortName("A" * 31)


def test_short_name_string_representation_returns_value() -> None:
    name = ShortName("PSG")

    assert str(name) == "PSG"