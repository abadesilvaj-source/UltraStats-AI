"""Testes de Probability."""

from decimal import Decimal

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.probability import Probability


@pytest.mark.parametrize("value", [0, "0.25", 0.5, 1])
def test_probability_accepts_values_between_zero_and_one(
    value: object,
) -> None:
    probability = Probability(value)  # type: ignore[arg-type]

    assert Decimal("0") <= probability.value <= Decimal("1")


@pytest.mark.parametrize("value", [-0.01, "1.01", 2])
def test_probability_rejects_values_outside_range(value: object) -> None:
    with pytest.raises(
        DomainValidationError,
        match="Probability deve estar entre 0 e 1",
    ):
        Probability(value)  # type: ignore[arg-type]