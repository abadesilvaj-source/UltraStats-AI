"""Testes de EventType."""

import pytest

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.event_type import EventType
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_event_type_inherits_from_domain_enum() -> None:
    assert issubclass(EventType, DomainEnum)


def test_event_type_contains_expected_values() -> None:
    assert EventType.values() == (
        "goal",
        "own_goal",
        "penalty_goal",
        "penalty_missed",
        "yellow_card",
        "second_yellow_card",
        "red_card",
        "substitution",
        "injury",
        "offside",
        "foul",
        "corner",
        "free_kick",
        "penalty_awarded",
        "kickoff",
        "half_time",
        "full_time",
        "extra_time_start",
        "extra_time_end",
        "penalty_shootout_start",
        "penalty_shootout_end",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("goal", EventType.GOAL),
        ("OWN GOAL", EventType.OWN_GOAL),
        ("penalty-goal", EventType.PENALTY_GOAL),
        ("Penalty Missed", EventType.PENALTY_MISSED),
        ("yellow card", EventType.YELLOW_CARD),
        (
            "SECOND_YELLOW_CARD",
            EventType.SECOND_YELLOW_CARD,
        ),
        ("red-card", EventType.RED_CARD),
        ("substitution", EventType.SUBSTITUTION),
        ("free kick", EventType.FREE_KICK),
        (
            "Penalty Shootout Start",
            EventType.PENALTY_SHOOTOUT_START,
        ),
    ],
)
def test_event_type_parses_valid_values(
    value: str,
    expected: EventType,
) -> None:
    assert EventType.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "assist",
        "save",
        "unknown_event",
    ],
)
def test_event_type_rejects_invalid_values(value: str) -> None:
    with pytest.raises(DomainValidationError):
        EventType.parse(value)


def test_event_type_has_value_accepts_normalized_input() -> None:
    assert EventType.has_value("Extra Time Start")
    assert EventType.has_value("PENALTY-SHOOTOUT-END")
    assert not EventType.has_value("unknown")


def test_event_type_is_serializable_as_string() -> None:
    assert str(EventType.GOAL) == "goal"