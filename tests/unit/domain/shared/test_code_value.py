"""Testes do tipo base CodeValue."""

import pytest

from ultrastats_ai.domain.shared import CodeValue, TextValue
from ultrastats_ai.domain.shared.codes import (
    CodeValue as CodesPackageCodeValue,
)


def test_code_value_inherits_from_text_value() -> None:
    code = CodeValue("BRA")

    assert isinstance(code, TextValue)


def test_code_value_removes_surrounding_whitespace() -> None:
    code = CodeValue("  BRA  ")

    assert code.value == "BRA"


def test_code_value_normalizes_to_uppercase() -> None:
    code = CodeValue("br-serie-a")

    assert code.value == "BR-SERIE-A"


@pytest.mark.parametrize(
    "value",
    [
        "BRA",
        "BR_SERIE_A",
        "BR-SERIE-A",
        "BR.SERIE.A",
        "UEFA2026",
        "1_DIVISION",
    ],
)
def test_code_value_accepts_supported_characters(value: str) -> None:
    code = CodeValue(value)

    assert code.value == value.upper()


@pytest.mark.parametrize(
    "value",
    [
        "BR SERIE A",
        "BR/SERIE/A",
        "BR@SERIE",
        "BR:SERIE",
        "SÉRIE_A",
        "BR#1",
    ],
)
def test_code_value_rejects_unsupported_characters(value: str) -> None:
    with pytest.raises(ValueError):
        CodeValue(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "     ",
    ],
)
def test_code_value_rejects_empty_values(value: str) -> None:
    with pytest.raises(ValueError):
        CodeValue(value)


def test_code_value_rejects_non_string_value() -> None:
    with pytest.raises(TypeError):
        CodeValue(123)  # type: ignore[arg-type]


def test_code_value_rejects_values_longer_than_maximum() -> None:
    value = "A" * 65

    with pytest.raises(ValueError):
        CodeValue(value)


def test_code_value_accepts_value_at_maximum_length() -> None:
    value = "A" * 64

    code = CodeValue(value)

    assert code.value == value


def test_code_value_equality_uses_normalized_value() -> None:
    first = CodeValue("bra")
    second = CodeValue("BRA")

    assert first == second
    assert hash(first) == hash(second)


def test_code_value_is_immutable() -> None:
    code = CodeValue("BRA")

    with pytest.raises((AttributeError, TypeError)):
        code.value = "ARG"


def test_public_apis_export_same_code_value_class() -> None:
    assert CodeValue is CodesPackageCodeValue