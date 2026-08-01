"""Testes de InterruptionType."""

import pytest

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.interruption_type import (
    InterruptionType,
)
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_interruption_type_inherits_from_domain_enum() -> None:
    assert issubclass(InterruptionType, DomainEnum)


def test_interruption_type_contains_expected_values() -> None:
    assert InterruptionType.values() == (
        "injury",
        "weather",
        "crowd_trouble",
        "pitch_invasion",
        "technical_issue",
        "lighting_failure",
        "security_issue",
        "referee_decision",
        "var_check",
        "medical_emergency",
        "equipment_failure",
        "other",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("injury", InterruptionType.INJURY),
        ("WEATHER", InterruptionType.WEATHER),
        (
            "Crowd Trouble",
            InterruptionType.CROWD_TROUBLE,
        ),
        (
            "pitch-invasion",
            InterruptionType.PITCH_INVASION,
        ),
        (
            "Technical Issue",
            InterruptionType.TECHNICAL_ISSUE,
        ),
        (
            "LIGHTING_FAILURE",
            InterruptionType.LIGHTING_FAILURE,
        ),
        ("var check", InterruptionType.VAR_CHECK),
        (
            "Medical Emergency",
            InterruptionType.MEDICAL_EMERGENCY,
        ),
    ],
)
def test_interruption_type_parses_valid_values(
    value: str,
    expected: InterruptionType,
) -> None:
    assert InterruptionType.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "pause",
        "break",
        "unknown_interruption",
    ],
)
def test_interruption_type_rejects_invalid_values(
    value: str,
) -> None:
    with pytest.raises(DomainValidationError):
        InterruptionType.parse(value)


def test_interruption_type_returns_expected_choices() -> None:
    assert (
        "var_check",
        "VAR_CHECK",
    ) in InterruptionType.choices()


def test_interruption_type_is_serializable_as_string() -> None:
    assert str(InterruptionType.WEATHER) == "weather"