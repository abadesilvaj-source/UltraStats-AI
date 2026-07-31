"""Testes de PredictionStatus."""

import pytest

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.prediction_status import (
    PredictionStatus,
)
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_prediction_status_inherits_from_domain_enum() -> None:
    assert issubclass(PredictionStatus, DomainEnum)


def test_prediction_status_contains_expected_values() -> None:
    assert PredictionStatus.values() == (
        "pending",
        "processing",
        "completed",
        "cancelled",
        "expired",
        "failed",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("pending", PredictionStatus.PENDING),
        ("PENDING", PredictionStatus.PENDING),
        (" processing ", PredictionStatus.PROCESSING),
        ("Completed", PredictionStatus.COMPLETED),
        ("cancelled", PredictionStatus.CANCELLED),
        ("EXPIRED", PredictionStatus.EXPIRED),
        ("failed", PredictionStatus.FAILED),
    ],
)
def test_prediction_status_parses_valid_values(
    value: str,
    expected: PredictionStatus,
) -> None:
    assert PredictionStatus.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "ready",
        "running",
        "unknown_prediction_status",
    ],
)
def test_prediction_status_rejects_invalid_values(
    value: str,
) -> None:
    with pytest.raises(DomainValidationError):
        PredictionStatus.parse(value)


def test_prediction_status_has_value_handles_invalid_types() -> None:
    assert PredictionStatus.has_value("processing")
    assert not PredictionStatus.has_value(123)
    assert not PredictionStatus.has_value(None)


def test_prediction_status_returns_expected_names() -> None:
    assert PredictionStatus.names() == (
        "PENDING",
        "PROCESSING",
        "COMPLETED",
        "CANCELLED",
        "EXPIRED",
        "FAILED",
    )


def test_prediction_status_is_serializable_as_string() -> None:
    assert str(PredictionStatus.COMPLETED) == "completed"