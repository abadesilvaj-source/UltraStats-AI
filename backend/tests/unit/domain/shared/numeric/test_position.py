"""Testes de Position."""

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.position import Position


@pytest.mark.parametrize("value", [1, "2", 100])
def test_position_accepts_positive_values(value: int | str) -> None:
    assert Position(value).value >= 1


@pytest.mark.parametrize("value", [0, -1])
def test_position_rejects_non_positive_values(value: int) -> None:
    with pytest.raises(
        DomainValidationError,
        match="maior ou igual a 1",
    ):
        Position(value)