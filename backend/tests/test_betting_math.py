import pytest

from app.utils.betting_math import (
    calculate_expected_value,
    calculate_implied_probability,
    calculate_potential_profit,
)


def test_implied_probability() -> None:
    result = calculate_implied_probability(2.00)

    assert result == pytest.approx(0.50)


def test_positive_expected_value() -> None:
    result = calculate_expected_value(
        probability=0.60,
        odd_value=2.00,
    )

    assert result == pytest.approx(0.20)


def test_negative_expected_value() -> None:
    result = calculate_expected_value(
        probability=0.40,
        odd_value=2.00,
    )

    assert result == pytest.approx(-0.20)


def test_potential_profit() -> None:
    result = calculate_potential_profit(
        odd_value=2.50,
        stake_units=2.00,
    )

    assert result == pytest.approx(3.00)


def test_invalid_odd() -> None:
    with pytest.raises(ValueError):
        calculate_implied_probability(1.00)