"""Testes de Age."""

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.age import Age


@pytest.mark.parametrize("value", [0, 18, "25", 130])
def test_age_accepts_values_between_zero_and_one_hundred_thirty(
    value: int | str,
) -> None:
    age = Age(value)

    assert 0 <= age.value <= 130


@pytest.mark.parametrize("value", [-1, 131])
def test_age_rejects_values_outside_range(value: int) -> None:
    with pytest.raises(
        DomainValidationError,
        match="Age deve estar entre 0 e 130",
    ):
        Age(value)