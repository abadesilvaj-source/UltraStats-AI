"""Testes do tipo Result."""

import pytest

from ultrastats_ai.domain.shared.errors import ResultAccessError
from ultrastats_ai.domain.shared.result import Result


def test_success_result_exposes_value() -> None:
    result = Result[int, str].success(10)

    assert result.is_success is True
    assert result.is_failure is False
    assert result.value == 10


def test_failure_result_exposes_error() -> None:
    result = Result[int, str].failure("invalid-operation")

    assert result.is_success is False
    assert result.is_failure is True
    assert result.error == "invalid-operation"


def test_failure_result_does_not_allow_value_access() -> None:
    result = Result[int, str].failure("invalid-operation")

    with pytest.raises(ResultAccessError):
        _ = result.value


def test_success_result_does_not_allow_error_access() -> None:
    result = Result[int, str].success(10)

    with pytest.raises(ResultAccessError):
        _ = result.error


def test_value_or_returns_success_value() -> None:
    result = Result[int, str].success(10)

    assert result.value_or(99) == 10


def test_value_or_returns_default_after_failure() -> None:
    result = Result[int, str].failure("invalid-operation")

    assert result.value_or(99) == 99


def test_failure_requires_an_error() -> None:
    with pytest.raises(
        ValueError,
        match="O erro do resultado não pode ser None.",
    ):
        Result[int, str].failure(None)  # type: ignore[arg-type]


def test_success_constructor_rejects_error_payload() -> None:
    with pytest.raises(ValueError, match="sucesso não pode possuir erro"):
        Result[int, str](
            _value=10,
            _error="invalid",
            _is_success=True,
        )


def test_failure_constructor_requires_error_payload() -> None:
    with pytest.raises(ValueError, match="falha deve possuir um erro"):
        Result[int, str](
            _value=None,
            _error=None,
            _is_success=False,
        )
