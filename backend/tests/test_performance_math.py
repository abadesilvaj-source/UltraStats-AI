import pytest

from app.utils.performance_math import (
    calculate_average,
    calculate_roi,
    calculate_win_rate,
)


def test_calculate_roi_positive() -> None:
    result = calculate_roi(
        total_profit=2.0,
        total_stake=10.0,
    )

    assert result == pytest.approx(20.0)


def test_calculate_roi_negative() -> None:
    result = calculate_roi(
        total_profit=-2.0,
        total_stake=10.0,
    )

    assert result == pytest.approx(-20.0)


def test_calculate_roi_without_stake() -> None:
    result = calculate_roi(
        total_profit=0.0,
        total_stake=0.0,
    )

    assert result == 0.0


def test_calculate_win_rate() -> None:
    result = calculate_win_rate(
        won_bets=6,
        lost_bets=4,
    )

    assert result == pytest.approx(60.0)


def test_calculate_win_rate_without_bets() -> None:
    result = calculate_win_rate(
        won_bets=0,
        lost_bets=0,
    )

    assert result == 0.0


def test_calculate_average() -> None:
    result = calculate_average(
        total_value=10.0,
        quantity=4,
    )

    assert result == pytest.approx(2.5)