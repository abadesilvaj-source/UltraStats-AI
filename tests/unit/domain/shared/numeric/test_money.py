"""Testes de Money."""

from decimal import Decimal

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.money import Money


def test_money_normalizes_amount_and_currency() -> None:
    money = Money("10.50", " brl ")

    assert money.amount == Decimal("10.50")
    assert money.currency == "BRL"


@pytest.mark.parametrize("currency", ["", "BR", "REAL", "B1L", "R$"])
def test_money_rejects_invalid_currency(currency: str) -> None:
    with pytest.raises(
        DomainValidationError,
        match="exatamente três letras",
    ):
        Money("10", currency)


def test_money_rejects_non_string_currency() -> None:
    with pytest.raises(TypeError, match="deve ser uma string"):
        Money("10", 123)  # type: ignore[arg-type]


def test_money_accepts_negative_amount() -> None:
    money = Money("-10.50", "BRL")

    assert money.amount == Decimal("-10.50")
    assert money.is_negative is True


def test_money_adds_values_with_same_currency() -> None:
    first = Money("10.50", "BRL")
    second = Money("5.25", "brl")

    result = first.add(second)

    assert result == Money("15.75", "BRL")


def test_money_subtracts_values_with_same_currency() -> None:
    first = Money("10.50", "BRL")
    second = Money("5.25", "BRL")

    result = first.subtract(second)

    assert result == Money("5.25", "BRL")


def test_money_rejects_operation_with_different_currencies() -> None:
    brl = Money("10", "BRL")
    usd = Money("10", "USD")

    with pytest.raises(
        DomainValidationError,
        match="moedas diferentes",
    ):
        brl.add(usd)


def test_money_rejects_operation_with_non_money_value() -> None:
    with pytest.raises(TypeError, match="outro objeto Money"):
        Money("10", "BRL").add(10)  # type: ignore[arg-type]


def test_money_is_immutable() -> None:
    money = Money("10", "BRL")

    with pytest.raises((AttributeError, TypeError)):
        money.currency = "USD"  # type: ignore[misc]
