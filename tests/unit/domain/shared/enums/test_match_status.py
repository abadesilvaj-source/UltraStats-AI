"""Testes de MatchStatus."""

import pytest

from ultrastats_ai.domain.shared.enums.match_status import MatchStatus
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_match_status_contains_expected_values() -> None:
    assert MatchStatus.values() == (
        "scheduled",
        "postponed",
        "cancelled",
        "abandoned",
        "live",
        "half_time",
        "extra_time",
        "penalty_shootout",
        "finished",
        "awarded",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("scheduled", MatchStatus.SCHEDULED),
        ("POSTPONED", MatchStatus.POSTPONED),
        ("half time", MatchStatus.HALF_TIME),
        ("EXTRA-TIME", MatchStatus.EXTRA_TIME),
        (
            "Penalty Shootout",
            MatchStatus.PENALTY_SHOOTOUT,
        ),
        ("finished", MatchStatus.FINISHED),
        ("awarded", MatchStatus.AWARDED),
    ],
)
def test_match_status_parses_valid_values(
    value: str,
    expected: MatchStatus,
) -> None:
    assert MatchStatus.parse(value) is expected


def test_match_status_rejects_invalid_value() -> None:
    with pytest.raises(DomainValidationError):
        MatchStatus.parse("not_started")


def test_match_status_is_serializable_as_string() -> None:
    assert MatchStatus.LIVE.value == "live"
    assert str(MatchStatus.LIVE) == "live"