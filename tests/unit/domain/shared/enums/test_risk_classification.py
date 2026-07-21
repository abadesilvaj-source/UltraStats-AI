"""Testes de RiskClassification."""

import pytest

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.risk_classification import (
    RiskClassification,
)
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_risk_classification_inherits_from_domain_enum() -> None:
    assert issubclass(RiskClassification, DomainEnum)


def test_risk_classification_contains_expected_values() -> None:
    assert RiskClassification.values() == (
        "very_low",
        "low",
        "medium",
        "high",
        "very_high",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("very_low", RiskClassification.VERY_LOW),
        ("Very Low", RiskClassification.VERY_LOW),
        ("LOW", RiskClassification.LOW),
        (" medium ", RiskClassification.MEDIUM),
        ("high", RiskClassification.HIGH),
        ("very-high", RiskClassification.VERY_HIGH),
    ],
)
def test_risk_classification_parses_valid_values(
    value: str,
    expected: RiskClassification,
) -> None:
    assert RiskClassification.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "minimal",
        "extreme",
        "unknown_risk",
    ],
)
def test_risk_classification_rejects_invalid_values(
    value: str,
) -> None:
    with pytest.raises(DomainValidationError):
        RiskClassification.parse(value)


def test_risk_classification_returns_expected_choices() -> None:
    assert RiskClassification.choices() == (
        ("very_low", "VERY_LOW"),
        ("low", "LOW"),
        ("medium", "MEDIUM"),
        ("high", "HIGH"),
        ("very_high", "VERY_HIGH"),
    )


def test_risk_classification_has_value_handles_invalid_types() -> None:
    assert RiskClassification.has_value("Very High")
    assert not RiskClassification.has_value(10)
    assert not RiskClassification.has_value(None)


def test_risk_classification_is_serializable_as_string() -> None:
    assert str(RiskClassification.MEDIUM) == "medium"