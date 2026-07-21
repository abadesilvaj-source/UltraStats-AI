"""Testes de Odds."""

from decimal import Decimal

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.odds import Odds


@pytest.mark.parametrize("value", ["1.01", 1.5, 2, "10.75"])
def test_odds_accepts_values_greater_than_one(value: object) -> None:
    odds = Odds(value)  # type: ignore[arg-type]

    assert odds.value > Decimal("1")


@pytest.mark.parametrize("value", [0, 1, "1.0", -2])
def test_odds_rejects_values_not_greater_than_one(value: object) -> None:
    with pytest.raises(
        DomainValidationError,
        match="Odds deve ser maior que 1",
    ):
        Odds(value)  # type: ignore[arg-type]


def test_odds_calculates_implied_probability() -> None:
    odds = Odds("2")

    assert odds.implied_probability == Decimal("0.5")