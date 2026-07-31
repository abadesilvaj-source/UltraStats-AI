"""Modelo canônico de bookmakers, mercados, seleções e odds."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared import (
    BettingMarketId,
    BettingSelectionId,
    BookmakerId,
    DecimalValue,
    MarketType,
    MatchId,
    Odds,
    OddsSnapshotId,
    UtcTimestamp,
)
from ultrastats_ai.domain.shared.errors import DomainError


class BettingDomainError(DomainError):
    """Erro-base do Betting Context."""


class InvalidBettingEntityError(BettingDomainError):
    """Indica entidade de mercado inconsistente."""


def _required(value: object, expected: type, field: str) -> None:
    if not isinstance(value, expected):
        raise TypeError(f"{field} deve ser {expected.__name__}.")


@dataclass(frozen=True, slots=True)
class Bookmaker:
    id: BookmakerId
    name: str
    slug: str
    is_active: bool = True

    def __post_init__(self) -> None:
        _required(self.id, BookmakerId, "id")
        _required(self.name, str, "name")
        _required(self.slug, str, "slug")
        _required(self.is_active, bool, "is_active")
        if not self.name.strip() or not self.slug.strip():
            raise InvalidBettingEntityError("Nome e slug são obrigatórios.")


@dataclass(frozen=True, slots=True)
class BettingSelection:
    id: BettingSelectionId
    market_id: BettingMarketId
    key: str
    label: str
    line: DecimalValue | None = None

    def __post_init__(self) -> None:
        _required(self.id, BettingSelectionId, "id")
        _required(self.market_id, BettingMarketId, "market_id")
        _required(self.key, str, "key")
        _required(self.label, str, "label")
        if self.line is not None:
            _required(self.line, DecimalValue, "line")
        if not self.key.strip() or not self.label.strip():
            raise InvalidBettingEntityError("Seleção exige chave e rótulo.")


@dataclass(frozen=True, slots=True)
class BettingMarket:
    id: BettingMarketId
    match_id: MatchId
    market_type: MarketType
    name: str
    selections: tuple[BettingSelection, ...]

    def __post_init__(self) -> None:
        _required(self.id, BettingMarketId, "id")
        _required(self.match_id, MatchId, "match_id")
        _required(self.market_type, MarketType, "market_type")
        _required(self.name, str, "name")
        _required(self.selections, tuple, "selections")
        if not self.name.strip() or not self.selections:
            raise InvalidBettingEntityError(
                "Mercado exige nome e ao menos uma seleção."
            )
        ids: set[BettingSelectionId] = set()
        keys: set[str] = set()
        for selection in self.selections:
            _required(selection, BettingSelection, "selection")
            if selection.market_id != self.id:
                raise InvalidBettingEntityError(
                    "Seleção pertence a outro mercado."
                )
            normalized_key = selection.key.strip().casefold()
            if selection.id in ids or normalized_key in keys:
                raise InvalidBettingEntityError("Seleção duplicada.")
            ids.add(selection.id)
            keys.add(normalized_key)


@dataclass(frozen=True, slots=True)
class OddsSnapshot:
    id: OddsSnapshotId
    bookmaker_id: BookmakerId
    market_id: BettingMarketId
    selection_id: BettingSelectionId
    odds: Odds
    observed_at: UtcTimestamp
    is_available: bool = True

    def __post_init__(self) -> None:
        _required(self.id, OddsSnapshotId, "id")
        _required(self.bookmaker_id, BookmakerId, "bookmaker_id")
        _required(self.market_id, BettingMarketId, "market_id")
        _required(self.selection_id, BettingSelectionId, "selection_id")
        _required(self.odds, Odds, "odds")
        _required(self.observed_at, UtcTimestamp, "observed_at")
        _required(self.is_available, bool, "is_available")
