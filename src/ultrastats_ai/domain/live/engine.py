"""Estado, ingestão, segurança e projeções determinísticas para partidas ao vivo."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Mapping


ZERO = Decimal("0")
ONE = Decimal("1")


class LiveEventType(StrEnum):
    SCORE = "score"
    CLOCK = "clock"
    STATISTIC = "statistic"
    ODDS = "odds"
    SUSPEND = "suspend"
    RESUME = "resume"
    FINISH = "finish"
    HEARTBEAT = "heartbeat"


class LivePhase(StrEnum):
    LIVE = "live"
    SUSPENDED = "suspended"
    FINISHED = "finished"


class LiveHealth(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class LiveEvent:
    event_id: str
    match_id: str
    kind: LiveEventType
    occurred_at: datetime
    received_at: datetime
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        if not self.event_id.strip() or not self.match_id.strip():
            raise ValueError("Evento ao vivo exige identidades.")
        if self.received_at < self.occurred_at:
            raise ValueError("Evento não pode ser recebido antes de ocorrer.")


@dataclass(frozen=True, slots=True)
class LiveRecommendation:
    selection: str
    probability: Decimal
    odds: Decimal
    expected_value: Decimal


@dataclass(frozen=True, slots=True)
class LiveMatchState:
    match_id: str
    phase: LivePhase
    health: LiveHealth
    minute: int
    home_score: int
    away_score: int
    statistics: Mapping[str, Decimal]
    odds: Mapping[str, Decimal]
    probabilities: Mapping[str, Decimal]
    recommendations: tuple[LiveRecommendation, ...]
    anomalies: tuple[str, ...]
    push_messages: tuple[str, ...]
    processed_event_ids: tuple[str, ...]
    last_event_at: datetime | None
    revision: int


@dataclass(frozen=True, slots=True)
class LivePolicy:
    maximum_event_lag: timedelta = timedelta(seconds=30)
    maximum_odds_ratio: Decimal = Decimal("2")
    minimum_recommendation_ev: Decimal = Decimal(".03")

    def __post_init__(self) -> None:
        if self.maximum_event_lag <= timedelta(0):
            raise ValueError("Atraso máximo deve ser positivo.")
        if self.maximum_odds_ratio <= ONE:
            raise ValueError("Razão máxima de odds deve ser maior que um.")
        if self.minimum_recommendation_ev < ZERO:
            raise ValueError("EV mínimo não pode ser negativo.")


class LiveEngine:
    def __init__(self, policy: LivePolicy = LivePolicy()) -> None:
        self.policy = policy

    @staticmethod
    def initial(match_id: str) -> LiveMatchState:
        if not match_id.strip():
            raise ValueError("Estado ao vivo exige partida.")
        return LiveMatchState(
            match_id,
            LivePhase.LIVE,
            LiveHealth.HEALTHY,
            0,
            0,
            0,
            {},
            {},
            {"home": Decimal(".35"), "draw": Decimal(".30"), "away": Decimal(".35")},
            (),
            (),
            (),
            (),
            None,
            0,
        )

    def ingest(self, state: LiveMatchState, event: LiveEvent) -> LiveMatchState:
        if event.match_id != state.match_id:
            raise ValueError("Evento pertence a outra partida.")
        if event.event_id in state.processed_event_ids:
            return state
        if state.phase is LivePhase.FINISHED:
            return self._blocked(state, event, "event_after_finish")

        anomalies = list(state.anomalies)
        pushes = list(state.push_messages)
        phase = state.phase
        health = LiveHealth.HEALTHY
        minute = state.minute
        home_score, away_score = state.home_score, state.away_score
        statistics = dict(state.statistics)
        odds = dict(state.odds)

        if state.last_event_at is not None and event.occurred_at < state.last_event_at:
            anomalies.append("out_of_order_event")
        lag = event.received_at - event.occurred_at
        if lag > self.policy.maximum_event_lag:
            anomalies.append("late_event")

        if event.kind is LiveEventType.SCORE:
            home, away = self._score(event.payload)
            if home < home_score or away < away_score:
                anomalies.append("score_regression")
            else:
                if home > home_score or away > away_score:
                    pushes.append(f"goal:{home}-{away}")
                home_score, away_score = home, away
        elif event.kind is LiveEventType.CLOCK:
            proposed = self._minute(event.payload)
            if proposed < minute:
                anomalies.append("clock_regression")
            else:
                minute = proposed
        elif event.kind is LiveEventType.STATISTIC:
            name, value = self._statistic(event.payload)
            statistics[name] = value
        elif event.kind is LiveEventType.ODDS:
            proposed = self._odds(event.payload)
            if any(
                selection in odds
                and max(value / odds[selection], odds[selection] / value)
                > self.policy.maximum_odds_ratio
                for selection, value in proposed.items()
            ):
                anomalies.append("odds_jump")
            else:
                odds.update(proposed)
        elif event.kind is LiveEventType.SUSPEND:
            phase, health = LivePhase.SUSPENDED, LiveHealth.BLOCKED
            pushes.append("match_suspended")
        elif event.kind is LiveEventType.RESUME:
            phase, health = LivePhase.LIVE, LiveHealth.HEALTHY
            pushes.append("match_resumed")
        elif event.kind is LiveEventType.FINISH:
            phase, health = LivePhase.FINISHED, LiveHealth.BLOCKED
            minute = max(minute, 90)
            pushes.append("match_finished")

        critical = {"out_of_order_event", "score_regression", "clock_regression", "odds_jump"}
        if critical.intersection(anomalies[len(state.anomalies) :]):
            phase, health = LivePhase.SUSPENDED, LiveHealth.BLOCKED
            pushes.append("automatic_suspension")
        elif "late_event" in anomalies[len(state.anomalies) :] and phase is LivePhase.LIVE:
            health = LiveHealth.DEGRADED

        probabilities = self._probabilities(home_score, away_score, minute)
        recommendations = self._recommendations(probabilities, odds, phase, health)
        if recommendations:
            pushes.append("live_recommendations_updated")
        return LiveMatchState(
            state.match_id,
            phase,
            health,
            minute,
            home_score,
            away_score,
            statistics,
            odds,
            probabilities,
            recommendations,
            tuple(anomalies),
            tuple(pushes),
            (*state.processed_event_ids, event.event_id),
            max(state.last_event_at, event.occurred_at)
            if state.last_event_at is not None
            else event.occurred_at,
            state.revision + 1,
        )

    def refresh(self, state: LiveMatchState, now: datetime) -> LiveMatchState:
        if state.phase is not LivePhase.LIVE or state.last_event_at is None:
            return state
        age = now - state.last_event_at
        if age <= self.policy.maximum_event_lag:
            return state
        if age <= self.policy.maximum_event_lag * 2:
            return replace(
                state,
                health=LiveHealth.DEGRADED,
                recommendations=(),
                revision=state.revision + 1,
            )
        return replace(
            state,
            phase=LivePhase.SUSPENDED,
            health=LiveHealth.BLOCKED,
            recommendations=(),
            anomalies=(*state.anomalies, "feed_timeout"),
            push_messages=(*state.push_messages, "automatic_suspension"),
            revision=state.revision + 1,
        )

    @staticmethod
    def _score(payload: Mapping[str, object]) -> tuple[int, int]:
        home, away = payload.get("home"), payload.get("away")
        if not isinstance(home, int) or not isinstance(away, int) or home < 0 or away < 0:
            raise ValueError("Placar ao vivo inválido.")
        return home, away

    @staticmethod
    def _minute(payload: Mapping[str, object]) -> int:
        minute = payload.get("minute")
        if not isinstance(minute, int) or not 0 <= minute <= 130:
            raise ValueError("Minuto ao vivo inválido.")
        return minute

    @staticmethod
    def _statistic(payload: Mapping[str, object]) -> tuple[str, Decimal]:
        name, raw = payload.get("name"), payload.get("value")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Estatística ao vivo exige nome.")
        try:
            value = Decimal(str(raw))
        except Exception as error:
            raise ValueError("Valor estatístico inválido.") from error
        if value < ZERO:
            raise ValueError("Valor estatístico inválido.")
        return name, value

    @staticmethod
    def _odds(payload: Mapping[str, object]) -> dict[str, Decimal]:
        values = {}
        for selection, raw in payload.items():
            if not isinstance(selection, str) or not selection.strip():
                raise ValueError("Seleção de odd ao vivo inválida.")
            try:
                value = Decimal(str(raw))
            except Exception as error:
                raise ValueError("Odd ao vivo inválida.") from error
            if value <= ONE:
                raise ValueError("Odd ao vivo inválida.")
            values[selection] = value
        if not values:
            raise ValueError("Odds ao vivo não podem ser vazias.")
        return values

    @staticmethod
    def _probabilities(home: int, away: int, minute: int) -> dict[str, Decimal]:
        remaining = max(ZERO, Decimal(90 - min(minute, 90)) / Decimal(90))
        difference = Decimal(home - away)
        draw = max(Decimal(".05"), Decimal(".30") * remaining)
        home_probability = max(
            Decimal(".02"),
            min(Decimal(".96"), Decimal(".35") + difference * Decimal(".22")),
        )
        away_probability = max(Decimal(".02"), ONE - home_probability - draw)
        total = home_probability + draw + away_probability
        return {
            "home": home_probability / total,
            "draw": draw / total,
            "away": away_probability / total,
        }

    def _recommendations(
        self,
        probabilities: Mapping[str, Decimal],
        odds: Mapping[str, Decimal],
        phase: LivePhase,
        health: LiveHealth,
    ) -> tuple[LiveRecommendation, ...]:
        if phase is not LivePhase.LIVE or health is not LiveHealth.HEALTHY:
            return ()
        recommendations = []
        for selection, offered in odds.items():
            if selection not in probabilities:
                continue
            expected_value = probabilities[selection] * offered - ONE
            if expected_value >= self.policy.minimum_recommendation_ev:
                recommendations.append(
                    LiveRecommendation(
                        selection,
                        probabilities[selection],
                        offered,
                        expected_value,
                    )
                )
        return tuple(
            sorted(recommendations, key=lambda item: (-item.expected_value, item.selection))
        )

    @staticmethod
    def _blocked(
        state: LiveMatchState,
        event: LiveEvent,
        anomaly: str,
    ) -> LiveMatchState:
        return replace(
            state,
            health=LiveHealth.BLOCKED,
            recommendations=(),
            anomalies=(*state.anomalies, anomaly),
            processed_event_ids=(*state.processed_event_ids, event.event_id),
            revision=state.revision + 1,
        )
