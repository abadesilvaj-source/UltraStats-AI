"""Testes de RoundNumber."""

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.round_number import RoundNumber


@pytest.mark.parametrize("value", [1, "10", 38])
def test_round_number_accepts_positive_values(value: int | str) -> None:
    assert RoundNumber(value).value >= 1


@pytest.mark.parametrize("value", [0, -1])
def test_round_number_rejects_non_positive_values(value: int) -> None:
    with pytest.raises(
        DomainValidationError,
        match="maior ou igual a 1",
    ):
        RoundNumber(value)