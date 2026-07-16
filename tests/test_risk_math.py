import pytest

from app.utils.risk_math import (
    apply_stake_cap,
    calculate_fractional_kelly,
    calculate_full_kelly_fraction,
    calculate_remaining_daily_exposure,
    calculate_stake_amount,
)


def test_full_kelly_positive() -> None:
    result = calculate_full_kelly_fraction(
        probability=0.55,
        odd_value=2.10,
    )

    assert result == pytest.approx(
        0.140909,
        rel=1e-4,
    )


def test_full_kelly_without_value() -> None:
    result = calculate_full_kelly_fraction(
        probability=0.40,
        odd_value=2.00,
    )

    assert result == 0.0


def test_fractional_kelly() -> None:
    result = calculate_fractional_kelly(
        probability=0.55,
        odd_value=2.10,
        kelly_multiplier=0.50,
    )

    assert result == pytest.approx(
        0.0704545,
        rel=1e-4,
    )


def test_calculate_stake_amount() -> None:
    result = calculate_stake_amount(
        bankroll_balance=1000.00,
        stake_fraction=0.02,
    )

    assert result == pytest.approx(20.00)


def test_apply_stake_cap() -> None:
    result = apply_stake_cap(
        bankroll_balance=1000.00,
        proposed_stake=70.00,
        max_stake_percentage=2.00,
    )

    assert result == pytest.approx(20.00)


def test_remaining_daily_exposure() -> None:
    result = calculate_remaining_daily_exposure(
        bankroll_balance=1000.00,
        current_daily_exposure=30.00,
        max_daily_exposure_percentage=5.00,
    )

    assert result == pytest.approx(20.00)