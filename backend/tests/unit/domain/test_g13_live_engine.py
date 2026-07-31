from datetime import datetime, timedelta, timezone
from decimal import Decimal as D

import pytest

from ultrastats_ai.domain.live import (
    LiveEngine,
    LiveEvent,
    LiveEventType,
    LiveHealth,
    LivePhase,
    LivePolicy,
)


NOW = datetime.now(timezone.utc)


def event(identifier, kind, payload=None, *, occurred=NOW, received=NOW, match="match"):
    return LiveEvent(identifier, match, kind, occurred, received, payload or {})


def test_policy_event_and_initial_validation() -> None:
    with pytest.raises(ValueError, match="Atraso"):
        LivePolicy(maximum_event_lag=timedelta(0))
    with pytest.raises(ValueError, match="Razão"):
        LivePolicy(maximum_odds_ratio=D("1"))
    with pytest.raises(ValueError, match="EV"):
        LivePolicy(minimum_recommendation_ev=D("-.1"))
    with pytest.raises(ValueError, match="identidades"):
        event("", LiveEventType.HEARTBEAT)
    with pytest.raises(ValueError, match="identidades"):
        event("id", LiveEventType.HEARTBEAT, match="")
    with pytest.raises(ValueError, match="antes"):
        event("id", LiveEventType.HEARTBEAT, occurred=NOW, received=NOW - timedelta(seconds=1))
    with pytest.raises(ValueError, match="partida"):
        LiveEngine.initial("")


def test_ingests_score_clock_statistics_odds_and_recommendations() -> None:
    engine = LiveEngine()
    state = engine.initial("match")
    state = engine.ingest(state, event("score", LiveEventType.SCORE, {"home": 1, "away": 0}))
    state = engine.ingest(
        state,
        event("clock", LiveEventType.CLOCK, {"minute": 35}, occurred=NOW + timedelta(seconds=1), received=NOW + timedelta(seconds=1)),
    )
    state = engine.ingest(
        state,
        event("stat", LiveEventType.STATISTIC, {"name": "shots", "value": "8"}, occurred=NOW + timedelta(seconds=2), received=NOW + timedelta(seconds=2)),
    )
    state = engine.ingest(
        state,
        event(
            "odds",
            LiveEventType.ODDS,
            {"home": "2.0", "draw": "5.0", "unknown": "2"},
            occurred=NOW + timedelta(seconds=3),
            received=NOW + timedelta(seconds=3),
        ),
    )
    assert (state.home_score, state.away_score, state.minute) == (1, 0, 35)
    assert state.statistics["shots"] == 8
    assert sum(state.probabilities.values(), D("0")) == 1
    assert state.recommendations
    assert all(item.selection != "unknown" for item in state.recommendations)
    assert state.push_messages[0] == "goal:1-0"
    assert state.push_messages[-1] == "live_recommendations_updated"
    assert state.revision == 4


def test_unchanged_score_does_not_emit_goal() -> None:
    state = LiveEngine().ingest(
        LiveEngine.initial("match"),
        event("score", LiveEventType.SCORE, {"home": 0, "away": 0}),
    )
    assert state.push_messages == ()
    assert (state.home_score, state.away_score) == (0, 0)


def test_duplicate_wrong_match_and_event_after_finish() -> None:
    engine = LiveEngine()
    state = engine.initial("match")
    heartbeat = event("heartbeat", LiveEventType.HEARTBEAT)
    updated = engine.ingest(state, heartbeat)
    assert engine.ingest(updated, heartbeat) is updated
    with pytest.raises(ValueError, match="outra"):
        engine.ingest(updated, event("other", LiveEventType.HEARTBEAT, match="other"))
    finished = engine.ingest(
        updated,
        event("finish", LiveEventType.FINISH, occurred=NOW + timedelta(seconds=1), received=NOW + timedelta(seconds=1)),
    )
    blocked = engine.ingest(
        finished,
        event("late", LiveEventType.HEARTBEAT, occurred=NOW + timedelta(seconds=2), received=NOW + timedelta(seconds=2)),
    )
    assert finished.phase is LivePhase.FINISHED and finished.minute == 90
    assert blocked.anomalies[-1] == "event_after_finish"
    assert blocked.health is LiveHealth.BLOCKED


def test_manual_suspend_and_resume() -> None:
    engine = LiveEngine()
    state = engine.ingest(engine.initial("match"), event("s", LiveEventType.SUSPEND))
    assert state.phase is LivePhase.SUSPENDED
    assert state.push_messages[-1] == "match_suspended"
    state = engine.ingest(
        state,
        event("r", LiveEventType.RESUME, occurred=NOW + timedelta(seconds=1), received=NOW + timedelta(seconds=1)),
    )
    assert state.phase is LivePhase.LIVE and state.health is LiveHealth.HEALTHY
    assert state.push_messages[-1] == "match_resumed"


@pytest.mark.parametrize(
    ("first", "second", "anomaly"),
    [
        (
            event("a", LiveEventType.SCORE, {"home": 1, "away": 0}),
            event("b", LiveEventType.SCORE, {"home": 0, "away": 0}, occurred=NOW + timedelta(seconds=1), received=NOW + timedelta(seconds=1)),
            "score_regression",
        ),
        (
            event("a", LiveEventType.CLOCK, {"minute": 20}),
            event("b", LiveEventType.CLOCK, {"minute": 19}, occurred=NOW + timedelta(seconds=1), received=NOW + timedelta(seconds=1)),
            "clock_regression",
        ),
        (
            event("a", LiveEventType.ODDS, {"home": "2"}),
            event("b", LiveEventType.ODDS, {"home": "5"}, occurred=NOW + timedelta(seconds=1), received=NOW + timedelta(seconds=1)),
            "odds_jump",
        ),
    ],
)
def test_critical_anomalies_suspend(first, second, anomaly) -> None:
    engine = LiveEngine()
    state = engine.ingest(engine.initial("match"), first)
    state = engine.ingest(state, second)
    assert anomaly in state.anomalies
    assert state.phase is LivePhase.SUSPENDED
    assert state.push_messages[-1] == "automatic_suspension"


def test_out_of_order_and_late_event_handling() -> None:
    engine = LiveEngine(LivePolicy(maximum_event_lag=timedelta(seconds=10)))
    state = engine.ingest(
        engine.initial("match"),
        event("first", LiveEventType.HEARTBEAT, occurred=NOW + timedelta(seconds=2), received=NOW + timedelta(seconds=2)),
    )
    state = engine.ingest(
        state,
        event("old", LiveEventType.HEARTBEAT, occurred=NOW, received=NOW + timedelta(seconds=11)),
    )
    assert {"out_of_order_event", "late_event"} <= set(state.anomalies)
    assert state.phase is LivePhase.SUSPENDED
    late = engine.ingest(
        engine.initial("match"),
        event("late", LiveEventType.HEARTBEAT, occurred=NOW, received=NOW + timedelta(seconds=11)),
    )
    assert late.health is LiveHealth.DEGRADED
    assert late.phase is LivePhase.LIVE


def test_refresh_healthy_degraded_blocked_and_inactive() -> None:
    engine = LiveEngine(LivePolicy(maximum_event_lag=timedelta(seconds=10)))
    initial = engine.initial("match")
    assert engine.refresh(initial, NOW) is initial
    state = engine.ingest(initial, event("heartbeat", LiveEventType.HEARTBEAT))
    assert engine.refresh(state, NOW + timedelta(seconds=10)) is state
    degraded = engine.refresh(state, NOW + timedelta(seconds=15))
    assert degraded.health is LiveHealth.DEGRADED
    blocked = engine.refresh(state, NOW + timedelta(seconds=21))
    assert blocked.phase is LivePhase.SUSPENDED
    assert blocked.anomalies[-1] == "feed_timeout"
    assert engine.refresh(blocked, NOW + timedelta(minutes=1)) is blocked


@pytest.mark.parametrize(
    "payload",
    [
        {"home": -1, "away": 0},
        {"home": "1", "away": 0},
        {"home": 1},
    ],
)
def test_invalid_score(payload) -> None:
    with pytest.raises(ValueError, match="Placar"):
        LiveEngine().ingest(LiveEngine.initial("match"), event("id", LiveEventType.SCORE, payload))


@pytest.mark.parametrize("payload", [{"minute": -1}, {"minute": 131}, {"minute": "1"}, {}])
def test_invalid_clock(payload) -> None:
    with pytest.raises(ValueError, match="Minuto"):
        LiveEngine().ingest(LiveEngine.initial("match"), event("id", LiveEventType.CLOCK, payload))


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"name": "", "value": 1}, "nome"),
        ({"name": 1, "value": 1}, "nome"),
        ({"name": "shots", "value": "x"}, "Valor"),
        ({"name": "shots", "value": -1}, "Valor"),
    ],
)
def test_invalid_statistic(payload, message) -> None:
    with pytest.raises(ValueError, match=message):
        LiveEngine().ingest(
            LiveEngine.initial("match"), event("id", LiveEventType.STATISTIC, payload)
        )


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "vazias"),
        ({"": "2"}, "Seleção"),
        ({1: "2"}, "Seleção"),
        ({"home": "x"}, "Odd"),
        ({"home": "1"}, "Odd"),
    ],
)
def test_invalid_odds(payload, message) -> None:
    with pytest.raises(ValueError, match=message):
        LiveEngine().ingest(LiveEngine.initial("match"), event("id", LiveEventType.ODDS, payload))


def test_probability_bounds_and_recommendation_filters() -> None:
    probabilities = LiveEngine._probabilities(10, 0, 100)
    assert all(D("0") < value < D("1") for value in probabilities.values())
    engine = LiveEngine()
    assert engine._recommendations(
        {"home": D(".5")},
        {"home": D("1.5")},
        LivePhase.LIVE,
        LiveHealth.HEALTHY,
    ) == ()
    assert engine._recommendations(
        {"home": D(".8")},
        {"home": D("2")},
        LivePhase.SUSPENDED,
        LiveHealth.BLOCKED,
    ) == ()
