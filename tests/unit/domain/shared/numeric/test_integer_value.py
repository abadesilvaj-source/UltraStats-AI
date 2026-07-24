"""Testes da classe-base IntegerValue."""

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.integer_value import IntegerValue


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (10, 10),
        ("10", 10),
        (" 10 ", 10),
        ("+10", 10),
        ("-10", -10),
    ],
)
def test_integer_value_normalizes_valid_inputs(
    value: int | str,
    expected: int,
) -> None:
    integer_value = IntegerValue(value)

    assert integer_value.value == expected
    assert isinstance(integer_value.value, int)


@pytest.mark.parametrize("value", ["", " ", "10.5", "abc", "1e2"])
def test_integer_value_rejects_invalid_strings(value: str) -> None:
    with pytest.raises(DomainValidationError):
        IntegerValue(value)


def test_integer_value_rejects_boolean() -> None:
    with pytest.raises(TypeError, match="valores booleanos"):
        IntegerValue(True)


def test_integer_value_rejects_unsupported_type() -> None:
    with pytest.raises(TypeError, match="int ou str"):
        IntegerValue(1.5)  # type: ignore[arg-type]


def test_integer_value_is_immutable() -> None:
    integer_value = IntegerValue(10)

    with pytest.raises((AttributeError, TypeError)):
        integer_value.value = 20  # type: ignore[misc]
