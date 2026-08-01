from datetime import datetime, timedelta
from decimal import Decimal

from app.models import Odd
from app.utils.odds_matching import (
    best_matching_odd,
    canonical_selection,
)


def odd(selection: str, value: str, age_hours: int = 0) -> Odd:
    return Odd(
        match_id=1,
        market_id=1,
        bookmaker="Book",
        selection=selection,
        odd_value=Decimal(value),
        collected_at=datetime(2026, 7, 30, 12) - timedelta(hours=age_hours),
    )


def test_canonical_selection_understands_provider_synonyms():
    assert canonical_selection("Mandante") == canonical_selection("Home")
    assert canonical_selection("Empate") == canonical_selection("Draw")
    assert canonical_selection("Mais de 2,5") == canonical_selection("Over 2.5")
    assert canonical_selection("Não") == canonical_selection("No")


def test_best_matching_odd_ignores_stale_and_chooses_best_current_price():
    now = datetime(2026, 7, 30, 12)
    result = best_matching_odd(
        [
            odd("Mandante", "2.05"),
            odd("Home", "2.15"),
            odd("Home", "3.50", age_hours=12),
        ],
        "Home",
        now=now,
        maximum_age_hours=6,
    )
    assert result is not None
    assert result.odd_value == Decimal("2.15")
