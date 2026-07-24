"""Testes da política de ciclo de vida da partida."""

import pytest

from ultrastats_ai.domain.match import can_transition
from ultrastats_ai.domain.shared import MatchStatus


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (MatchStatus.DATE_DEFINED, MatchStatus.SCHEDULED),
        (MatchStatus.TIME_UNCONFIRMED, MatchStatus.CONFIRMED),
        (MatchStatus.SCHEDULED, MatchStatus.WARMUP),
        (MatchStatus.CONFIRMED, MatchStatus.PRE_MATCH),
        (MatchStatus.PRE_MATCH, MatchStatus.FIRST_HALF),
        (MatchStatus.WARMUP, MatchStatus.LIVE),
        (MatchStatus.DELAYED, MatchStatus.POSTPONED),
        (MatchStatus.POSTPONED, MatchStatus.SCHEDULED),
        (MatchStatus.FIRST_HALF, MatchStatus.HALF_TIME),
        (MatchStatus.LIVE, MatchStatus.FINISHED),
        (MatchStatus.HALF_TIME, MatchStatus.SECOND_HALF),
        (MatchStatus.SECOND_HALF, MatchStatus.EXTRA_TIME),
        (
            MatchStatus.EXTRA_TIME,
            MatchStatus.EXTRA_TIME_HALF_TIME,
        ),
        (
            MatchStatus.EXTRA_TIME_HALF_TIME,
            MatchStatus.EXTRA_TIME,
        ),
        (
            MatchStatus.PENALTY_SHOOTOUT,
            MatchStatus.AFTER_PENALTIES,
        ),
        (MatchStatus.INTERRUPTED, MatchStatus.SUSPENDED),
        (MatchStatus.SUSPENDED, MatchStatus.ABANDONED),
        (MatchStatus.ABANDONED, MatchStatus.AWARDED),
        (MatchStatus.UNKNOWN, MatchStatus.DATE_DEFINED),
    ],
)
def test_documented_transitions_are_allowed(
    current: MatchStatus,
    target: MatchStatus,
) -> None:
    assert can_transition(current, target)


@pytest.mark.parametrize(
    "terminal",
    [
        MatchStatus.CANCELLED,
        MatchStatus.WALKOVER,
        MatchStatus.FINISHED,
        MatchStatus.AFTER_EXTRA_TIME,
        MatchStatus.AFTER_PENALTIES,
        MatchStatus.AWARDED,
    ],
)
def test_terminal_statuses_reject_automatic_transitions(
    terminal: MatchStatus,
) -> None:
    assert not can_transition(terminal, MatchStatus.LIVE)


def test_transition_to_same_status_is_not_allowed() -> None:
    assert not can_transition(
        MatchStatus.SCHEDULED,
        MatchStatus.SCHEDULED,
    )


def test_can_transition_rejects_invalid_current_type() -> None:
    with pytest.raises(TypeError, match="current"):
        can_transition(  # type: ignore[arg-type]
            "scheduled",
            MatchStatus.LIVE,
        )


def test_can_transition_rejects_invalid_target_type() -> None:
    with pytest.raises(TypeError, match="target"):
        can_transition(  # type: ignore[arg-type]
            MatchStatus.SCHEDULED,
            "live",
        )
