"""Testes de DecisionType."""

import pytest

from ultrastats_ai.domain.shared.enums.decision_type import DecisionType
from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_decision_type_inherits_from_domain_enum() -> None:
    assert issubclass(DecisionType, DomainEnum)


def test_decision_type_contains_expected_values() -> None:
    assert DecisionType.values() == (
        "confirmed",
        "overturned",
        "awarded",
        "disallowed",
        "cancelled",
        "suspended",
        "postponed",
        "abandoned",
        "rescheduled",
        "administrative_win",
        "administrative_draw",
        "points_deduction",
        "fine",
        "no_action",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("confirmed", DecisionType.CONFIRMED),
        ("OVERTURNED", DecisionType.OVERTURNED),
        ("awarded", DecisionType.AWARDED),
        ("Disallowed", DecisionType.DISALLOWED),
        ("rescheduled", DecisionType.RESCHEDULED),
        (
            "Administrative Win",
            DecisionType.ADMINISTRATIVE_WIN,
        ),
        (
            "administrative-draw",
            DecisionType.ADMINISTRATIVE_DRAW,
        ),
        (
            "POINTS DEDUCTION",
            DecisionType.POINTS_DEDUCTION,
        ),
        ("no action", DecisionType.NO_ACTION),
    ],
)
def test_decision_type_parses_valid_values(
    value: str,
    expected: DecisionType,
) -> None:
    assert DecisionType.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "approved",
        "rejected",
        "unknown_decision",
    ],
)
def test_decision_type_rejects_invalid_values(value: str) -> None:
    with pytest.raises(DomainValidationError):
        DecisionType.parse(value)


def test_decision_type_has_value_handles_invalid_types() -> None:
    assert DecisionType.has_value("administrative win")
    assert not DecisionType.has_value(123)
    assert not DecisionType.has_value(None)


def test_decision_type_is_serializable_as_string() -> None:
    assert str(DecisionType.CONFIRMED) == "confirmed"