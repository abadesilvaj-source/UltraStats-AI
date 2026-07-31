"""Preferências, descoberta, cenários, alertas e comunicação da experiência."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum
import unicodedata
from typing import Mapping


class ExperienceMode(StrEnum):
    SIMPLE = "simple"
    ADVANCED = "advanced"


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    PUSH = "push"


@dataclass(frozen=True, slots=True)
class UserExperienceProfile:
    user_id: str
    mode: ExperienceMode = ExperienceMode.SIMPLE
    locale: str = "pt-BR"
    reduced_motion: bool = False
    high_contrast: bool = False

    def __post_init__(self) -> None:
        if not self.user_id.strip() or not self.locale.strip():
            raise ValueError("Perfil de experiência exige usuário e idioma.")


@dataclass(frozen=True, slots=True)
class Favorite:
    user_id: str
    entity_type: str
    entity_id: str
    label: str

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (self.user_id, self.entity_type, self.entity_id, self.label)
        ):
            raise ValueError("Favorito exige usuário, entidade e rótulo.")


@dataclass(frozen=True, slots=True)
class AlertRule:
    alert_id: str
    user_id: str
    metric: str
    operator: str
    threshold: Decimal
    channel: NotificationChannel

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.alert_id, self.user_id, self.metric)):
            raise ValueError("Alerta exige identidade, usuário e métrica.")
        if self.operator not in {">", ">=", "<", "<=", "=="}:
            raise ValueError("Operador de alerta inválido.")

    def matches(self, value: Decimal) -> bool:
        operations = {
            ">": value > self.threshold,
            ">=": value >= self.threshold,
            "<": value < self.threshold,
            "<=": value <= self.threshold,
            "==": value == self.threshold,
        }
        return operations[self.operator]


@dataclass(frozen=True, slots=True)
class Notification:
    notification_id: str
    user_id: str
    title: str
    body: str
    channel: NotificationChannel
    created_at: datetime
    read: bool = False

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (self.notification_id, self.user_id, self.title, self.body)
        ):
            raise ValueError("Notificação exige identidade e conteúdo.")


@dataclass(frozen=True, slots=True)
class SearchDocument:
    entity_type: str
    entity_id: str
    title: str
    keywords: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.entity_type, self.entity_id, self.title)):
            raise ValueError("Documento de busca exige entidade e título.")


@dataclass(frozen=True, slots=True)
class SearchResult:
    document: SearchDocument
    relevance: int


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    probability: Decimal
    odds: Decimal
    stake: Decimal

    def __post_init__(self) -> None:
        if not self.name.strip() or not Decimal("0") <= self.probability <= Decimal("1"):
            raise ValueError("Cenário exige nome e probabilidade válida.")
        if self.odds <= 1 or self.stake < 0:
            raise ValueError("Cenário exige odd válida e stake não negativa.")

    @property
    def expected_profit(self) -> Decimal:
        return self.stake * (self.probability * self.odds - 1)


@dataclass(frozen=True, slots=True)
class ScenarioComparison:
    scenarios: tuple[Scenario, ...]
    best: Scenario | None


@dataclass(frozen=True, slots=True)
class TimelineItem:
    item_id: str
    category: str
    title: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class DataFreshness:
    updated_at: datetime
    now: datetime
    stale_after: timedelta = timedelta(minutes=15)

    def __post_init__(self) -> None:
        if self.stale_after <= timedelta(0):
            raise ValueError("Janela de atualização deve ser positiva.")

    @property
    def status(self) -> str:
        age = self.now - self.updated_at
        if age < timedelta(0):
            return "clock_skew"
        if age <= self.stale_after:
            return "fresh"
        return "stale"


def natural_language_search(
    query: str,
    documents: tuple[SearchDocument, ...],
) -> tuple[SearchResult, ...]:
    terms = set(_normalize(query).split())
    if not terms:
        return ()
    results = []
    for document in documents:
        title = _normalize(document.title)
        haystack = " ".join((title, *(_normalize(value) for value in document.keywords)))
        relevance = sum(2 if term in title else 1 for term in terms if term in haystack)
        if relevance:
            results.append(SearchResult(document, relevance))
    return tuple(
        sorted(
            results,
            key=lambda item: (-item.relevance, item.document.title, item.document.entity_id),
        )
    )


def compare_scenarios(scenarios: tuple[Scenario, ...]) -> ScenarioComparison:
    best = max(scenarios, key=lambda item: (item.expected_profit, item.name)) if scenarios else None
    return ScenarioComparison(scenarios, best)


def build_timeline(items: tuple[TimelineItem, ...]) -> tuple[TimelineItem, ...]:
    return tuple(sorted(items, key=lambda item: (-item.occurred_at.timestamp(), item.item_id)))


def automatic_report(
    title: str,
    metrics: Mapping[str, object],
    generated_at: datetime,
) -> str:
    if not title.strip() or not metrics:
        raise ValueError("Relatório exige título e métricas.")
    rows = "\n".join(f"- {key}: {metrics[key]}" for key in sorted(metrics))
    return f"# {title}\n\nGerado em: {generated_at.isoformat()}\n\n{rows}\n"


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(character for character in decomposed if not unicodedata.combining(character))
