"""Testes da infraestrutura textual compartilhada."""

from dataclasses import FrozenInstanceError
from typing import ClassVar, Pattern

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.text_value import (
    TextValue,
    compile_text_pattern,
)


class ShortText(TextValue):
    """Tipo textual utilizado nos testes."""

    MIN_LENGTH: ClassVar[int] = 2
    MAX_LENGTH: ClassVar[int] = 10


class CodeText(TextValue):
    """Código textual limitado a letras maiúsculas e números."""

    MIN_LENGTH: ClassVar[int] = 2
    MAX_LENGTH: ClassVar[int] = 8
    PATTERN: ClassVar[Pattern[str]] = compile_text_pattern(
        r"[A-Z0-9]+"
    )


class PreserveInternalWhitespaceText(TextValue):
    """Tipo que não reduz espaços internos."""

    COLLAPSE_WHITESPACE: ClassVar[bool] = False


def test_text_value_accepts_valid_string() -> None:
    text = ShortText("Football")

    assert text.value == "Football"


def test_text_value_removes_surrounding_spaces() -> None:
    text = ShortText("  Football  ")

    assert text.value == "Football"


def test_text_value_collapses_repeated_internal_spaces() -> None:
    text = TextValue("UltraStats    AI")

    assert text.value == "UltraStats AI"


def test_text_value_collapses_tabs_and_line_breaks() -> None:
    text = TextValue("UltraStats\t\nAI")

    assert text.value == "UltraStats AI"


def test_text_value_normalizes_unicode() -> None:
    text = TextValue("ＡＢＣ")

    assert text.value == "ABC"


def test_text_value_returns_normalized_string() -> None:
    text = TextValue("  UltraStats    AI  ")

    assert str(text) == "UltraStats AI"


def test_text_value_is_immutable() -> None:
    text = TextValue("UltraStats")

    with pytest.raises(FrozenInstanceError):
        text.value = "Other"  # type: ignore[misc]


def test_equal_text_values_have_equal_hashes() -> None:
    first = ShortText("Football")
    second = ShortText("  Football  ")

    assert first == second
    assert hash(first) == hash(second)


def test_different_text_value_types_are_not_equal() -> None:
    first = ShortText("Football")
    second = TextValue("Football")

    assert first != second


def test_text_value_can_be_used_as_dictionary_key() -> None:
    text = ShortText("Football")

    values = {
        text: "valid",
    }

    assert values[text] == "valid"


def test_text_value_rejects_non_string_value() -> None:
    with pytest.raises(
        DomainValidationError,
        match="deve receber uma string",
    ):
        TextValue(123)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "invalid_value",
    [
        "",
        " ",
        "   ",
        "\t",
        "\n",
    ],
)
def test_text_value_rejects_empty_normalized_value(
    invalid_value: str,
) -> None:
    with pytest.raises(
        DomainValidationError,
        match="não pode ser vazio",
    ):
        TextValue(invalid_value)


def test_text_value_rejects_value_below_minimum_length() -> None:
    with pytest.raises(
        DomainValidationError,
        match="pelo menos 2",
    ):
        ShortText("A")


def test_text_value_rejects_value_above_maximum_length() -> None:
    with pytest.raises(
        DomainValidationError,
        match="no máximo 10",
    ):
        ShortText("UltraStats AI")


def test_text_value_accepts_value_matching_pattern() -> None:
    code = CodeText("ABC123")

    assert code.value == "ABC123"


@pytest.mark.parametrize(
    "invalid_value",
    [
        "abc",
        "ABC-123",
        "ABC 123",
        "@ABC",
    ],
)
def test_text_value_rejects_value_not_matching_pattern(
    invalid_value: str,
) -> None:
    with pytest.raises(
        DomainValidationError,
        match="formato inválido",
    ):
        CodeText(invalid_value)


def test_text_value_can_preserve_internal_whitespace() -> None:
    text = PreserveInternalWhitespaceText("  UltraStats    AI  ")

    assert text.value == "UltraStats    AI"