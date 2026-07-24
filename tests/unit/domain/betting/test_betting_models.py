"""Testes do Betting Context."""

from dataclasses import replace

import pytest

from ultrastats_ai.domain.betting import (
    BettingMarket,
    BettingSelection,
    Bookmaker,
    InvalidBettingEntityError,
    OddsSnapshot,
)
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


def selection(
    market_id: BettingMarketId,
    *,
    key: str = "home",
    id: BettingSelectionId | None = None,
) -> BettingSelection:
    return BettingSelection(
        id=id or BettingSelectionId.new(),
        market_id=market_id,
        key=key,
        label=key.title(),
        line=DecimalValue("2.5"),
    )


def test_bookmaker_and_odds_snapshot_are_created() -> None:
    bookmaker = Bookmaker(
        BookmakerId.new(),
        "Casa",
        "casa",
    )
    market_id = BettingMarketId.new()
    item = selection(market_id)
    snapshot = OddsSnapshot(
        OddsSnapshotId.new(),
        bookmaker.id,
        market_id,
        item.id,
        Odds("2.10"),
        UtcTimestamp("2026-08-01T12:00:00Z"),
    )

    assert bookmaker.is_active
    assert snapshot.odds.implied_probability > 0


def test_bookmaker_requires_name_and_slug() -> None:
    with pytest.raises(InvalidBettingEntityError):
        Bookmaker(BookmakerId.new(), " ", " ")


def test_selection_requires_key_and_label() -> None:
    item = selection(BettingMarketId.new())
    assert replace(item, line=None).line is None

    with pytest.raises(InvalidBettingEntityError):
        replace(item, key="")
    with pytest.raises(TypeError, match="line"):
        replace(item, line=object())  # type: ignore[arg-type]


def test_market_validates_selections_and_ownership() -> None:
    market_id = BettingMarketId.new()
    home = selection(market_id)
    market = BettingMarket(
        market_id,
        MatchId.new(),
        MarketType.MATCH_WINNER,
        "Vencedor",
        (home,),
    )
    assert market.selections == (home,)

    with pytest.raises(InvalidBettingEntityError, match="nome"):
        replace(market, name="")
    with pytest.raises(TypeError, match="selection"):
        replace(market, selections=(object(),))  # type: ignore[arg-type]
    with pytest.raises(InvalidBettingEntityError, match="outro mercado"):
        replace(
            market,
            selections=(selection(BettingMarketId.new()),),
        )


@pytest.mark.parametrize("duplicate_kind", ["id", "key"])
def test_market_rejects_duplicate_selections(
    duplicate_kind: str,
) -> None:
    market_id = BettingMarketId.new()
    first = selection(market_id)
    second = selection(
        market_id,
        id=first.id if duplicate_kind == "id" else None,
        key="HOME" if duplicate_kind == "key" else "away",
    )

    with pytest.raises(InvalidBettingEntityError, match="duplicada"):
        BettingMarket(
            market_id,
            MatchId.new(),
            MarketType.MATCH_WINNER,
            "Vencedor",
            (first, second),
        )


def test_required_type_validation() -> None:
    with pytest.raises(TypeError, match="id"):
        Bookmaker(object(), "Casa", "casa")  # type: ignore[arg-type]
