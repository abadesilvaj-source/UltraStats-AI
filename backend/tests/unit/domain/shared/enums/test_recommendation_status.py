"""Testes de RecommendationStatus."""

import pytest

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.recommendation_status import (
    RecommendationStatus,
)
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_recommendation_status_inherits_from_domain_enum() -> None:
    assert issubclass(RecommendationStatus, DomainEnum)


def test_recommendation_status_contains_expected_values() -> None:
    assert RecommendationStatus.values() == (
        "draft",
        "published",
        "active",
        "expired",
        "cancelled",
        "archived",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("draft", RecommendationStatus.DRAFT),
        ("DRAFT", RecommendationStatus.DRAFT),
        (" published ", RecommendationStatus.PUBLISHED),
        ("Active", RecommendationStatus.ACTIVE),
        ("expired", RecommendationStatus.EXPIRED),
        ("CANCELLED", RecommendationStatus.CANCELLED),
        ("archived", RecommendationStatus.ARCHIVED),
    ],
)
def test_recommendation_status_parses_valid_values(
    value: str,
    expected: RecommendationStatus,
) -> None:
    assert RecommendationStatus.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "visible",
        "hidden",
        "unknown_recommendation_status",
    ],
)
def test_recommendation_status_rejects_invalid_values(
    value: str,
) -> None:
    with pytest.raises(DomainValidationError):
        RecommendationStatus.parse(value)


def test_recommendation_status_has_value_accepts_valid_input() -> None:
    assert RecommendationStatus.has_value("published")
    assert RecommendationStatus.has_value("ARCHIVED")
    assert not RecommendationStatus.has_value("unknown")


def test_recommendation_status_returns_expected_choices() -> None:
    assert RecommendationStatus.choices() == (
        ("draft", "DRAFT"),
        ("published", "PUBLISHED"),
        ("active", "ACTIVE"),
        ("expired", "EXPIRED"),
        ("cancelled", "CANCELLED"),
        ("archived", "ARCHIVED"),
    )


def test_recommendation_status_is_serializable_as_string() -> None:
    assert str(RecommendationStatus.ACTIVE) == "active"