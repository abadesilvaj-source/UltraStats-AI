"""Testes da classe-base DecimalValue."""

from decimal import Decimal

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.decimal_value import DecimalValue


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (10, Decimal("10")),
        (10.5, Decimal("10.5")),
        ("10.50", Decimal("10.50")),
        (" 10.50 ", Decimal("10.50")),
        (Decimal("2.75"), Decimal("2.75")),
    ],
)
def test_decimal_value_normalizes_valid_inputs(
    value: object,
    expected: Decimal,
) -> None:
    decimal_value = DecimalValue(value)  # type: ignore[arg-type]

    assert decimal_value.value == expected
    assert isinstance(decimal_value.value, Decimal)


@pytest.mark.parametrize("value", ["", " ", "abc", "1.2.3"])
def test_decimal_value_rejects_invalid_strings(value: str) -> None:
    with pytest.raises(DomainValidationError):
        DecimalValue(value)


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_decimal_value_rejects_non_finite_values(value: str) -> None:
    with pytest.raises(
        DomainValidationError,
        match="valor decimal finito",
    ):
        DecimalValue(value)


def test_decimal_value_rejects_boolean() -> None:
    with pytest.raises(TypeError, match="valores booleanos"):
        DecimalValue(True)


def test_decimal_value_rejects_unsupported_type() -> None:
    with pytest.raises(TypeError, match="Decimal, int, float ou str"):
        DecimalValue(object())  # type: ignore[arg-type]


def test_decimal_value_is_immutable() -> None:
    decimal_value = DecimalValue("10")

    with pytest.raises((AttributeError, TypeError)):
        decimal_value.value = Decimal("20")  # type: ignore[misc]
