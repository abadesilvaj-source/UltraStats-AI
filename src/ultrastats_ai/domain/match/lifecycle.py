"""Política canônica de transições do ciclo de vida da partida."""

from ultrastats_ai.domain.shared import MatchStatus


_ALLOWED_TRANSITIONS: dict[MatchStatus, frozenset[MatchStatus]] = {
    MatchStatus.DATE_DEFINED: frozenset(
        {
            MatchStatus.TIME_UNCONFIRMED,
            MatchStatus.SCHEDULED,
            MatchStatus.CANCELLED,
        }
    ),
    MatchStatus.TIME_UNCONFIRMED: frozenset(
        {
            MatchStatus.SCHEDULED,
            MatchStatus.CONFIRMED,
            MatchStatus.POSTPONED,
            MatchStatus.CANCELLED,
        }
    ),
    MatchStatus.SCHEDULED: frozenset(
        {
            MatchStatus.CONFIRMED,
            MatchStatus.PRE_MATCH,
            MatchStatus.WARMUP,
            MatchStatus.FIRST_HALF,
            MatchStatus.LIVE,
            MatchStatus.DELAYED,
            MatchStatus.POSTPONED,
            MatchStatus.CANCELLED,
            MatchStatus.WALKOVER,
            MatchStatus.AWARDED,
        }
    ),
    MatchStatus.CONFIRMED: frozenset(
        {
            MatchStatus.PRE_MATCH,
            MatchStatus.WARMUP,
            MatchStatus.FIRST_HALF,
            MatchStatus.LIVE,
            MatchStatus.DELAYED,
            MatchStatus.POSTPONED,
            MatchStatus.CANCELLED,
        }
    ),
    MatchStatus.PRE_MATCH: frozenset(
        {
            MatchStatus.WARMUP,
            MatchStatus.FIRST_HALF,
            MatchStatus.LIVE,
            MatchStatus.DELAYED,
            MatchStatus.POSTPONED,
            MatchStatus.CANCELLED,
        }
    ),
    MatchStatus.WARMUP: frozenset(
        {
            MatchStatus.FIRST_HALF,
            MatchStatus.LIVE,
            MatchStatus.DELAYED,
            MatchStatus.POSTPONED,
        }
    ),
    MatchStatus.DELAYED: frozenset(
        {
            MatchStatus.WARMUP,
            MatchStatus.FIRST_HALF,
            MatchStatus.LIVE,
            MatchStatus.POSTPONED,
            MatchStatus.CANCELLED,
        }
    ),
    MatchStatus.POSTPONED: frozenset(
        {
            MatchStatus.SCHEDULED,
            MatchStatus.CANCELLED,
        }
    ),
    MatchStatus.FIRST_HALF: frozenset(
        {
            MatchStatus.HALF_TIME,
            MatchStatus.INTERRUPTED,
            MatchStatus.SUSPENDED,
            MatchStatus.ABANDONED,
        }
    ),
    MatchStatus.LIVE: frozenset(
        {
            MatchStatus.HALF_TIME,
            MatchStatus.FINISHED,
            MatchStatus.INTERRUPTED,
            MatchStatus.SUSPENDED,
            MatchStatus.ABANDONED,
        }
    ),
    MatchStatus.HALF_TIME: frozenset(
        {
            MatchStatus.SECOND_HALF,
            MatchStatus.LIVE,
            MatchStatus.INTERRUPTED,
            MatchStatus.SUSPENDED,
            MatchStatus.ABANDONED,
        }
    ),
    MatchStatus.SECOND_HALF: frozenset(
        {
            MatchStatus.FINISHED,
            MatchStatus.EXTRA_TIME,
            MatchStatus.PENALTY_SHOOTOUT,
            MatchStatus.INTERRUPTED,
            MatchStatus.SUSPENDED,
            MatchStatus.ABANDONED,
        }
    ),
    MatchStatus.EXTRA_TIME: frozenset(
        {
            MatchStatus.EXTRA_TIME_HALF_TIME,
            MatchStatus.FINISHED,
            MatchStatus.AFTER_EXTRA_TIME,
            MatchStatus.PENALTY_SHOOTOUT,
            MatchStatus.INTERRUPTED,
            MatchStatus.SUSPENDED,
            MatchStatus.ABANDONED,
        }
    ),
    MatchStatus.EXTRA_TIME_HALF_TIME: frozenset(
        {
            MatchStatus.EXTRA_TIME,
            MatchStatus.SUSPENDED,
            MatchStatus.ABANDONED,
        }
    ),
    MatchStatus.PENALTY_SHOOTOUT: frozenset(
        {
            MatchStatus.FINISHED,
            MatchStatus.AFTER_PENALTIES,
            MatchStatus.INTERRUPTED,
            MatchStatus.SUSPENDED,
            MatchStatus.ABANDONED,
        }
    ),
    MatchStatus.INTERRUPTED: frozenset(
        {
            MatchStatus.FIRST_HALF,
            MatchStatus.SECOND_HALF,
            MatchStatus.EXTRA_TIME,
            MatchStatus.PENALTY_SHOOTOUT,
            MatchStatus.SUSPENDED,
            MatchStatus.ABANDONED,
            MatchStatus.AWARDED,
        }
    ),
    MatchStatus.SUSPENDED: frozenset(
        {
            MatchStatus.FIRST_HALF,
            MatchStatus.SECOND_HALF,
            MatchStatus.EXTRA_TIME,
            MatchStatus.PENALTY_SHOOTOUT,
            MatchStatus.ABANDONED,
            MatchStatus.AWARDED,
        }
    ),
    MatchStatus.ABANDONED: frozenset({MatchStatus.AWARDED}),
    MatchStatus.UNKNOWN: frozenset(
        {
            MatchStatus.DATE_DEFINED,
            MatchStatus.TIME_UNCONFIRMED,
            MatchStatus.SCHEDULED,
        }
    ),
}


def can_transition(
    current: MatchStatus,
    target: MatchStatus,
) -> bool:
    """Informa se a transição operacional está autorizada."""

    if not isinstance(current, MatchStatus):
        raise TypeError("current deve ser MatchStatus.")
    if not isinstance(target, MatchStatus):
        raise TypeError("target deve ser MatchStatus.")

    return target in _ALLOWED_TRANSITIONS.get(
        current,
        frozenset(),
    )
