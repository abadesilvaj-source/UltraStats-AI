import pytest

from app.utils.bankroll_math import (
    calculate_unit_value,
)


def test_calculate_unit_value() -> None:
    result = calculate_unit_value(
        bankroll_balance=1000.00,
        unit_percentage=1.00,
    )

    assert result == pytest.approx(10.00)


def test_half_percent_unit() -> None:
    result = calculate_unit_value(
        bankroll_balance=2000.00,
        unit_percentage=0.50,
    )

    assert result == pytest.approx(10.00)


def test_invalid_percentage() -> None:
    with pytest.raises(ValueError):
        calculate_unit_value(
            bankroll_balance=1000.00,
            unit_percentage=0.00,
        )


def test_negative_balance() -> None:
    with pytest.raises(ValueError):
        calculate_unit_value(
            bankroll_balance=-100.00,
            unit_percentage=1.00,
        )