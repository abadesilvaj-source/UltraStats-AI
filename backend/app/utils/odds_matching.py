from __future__ import annotations

from datetime import datetime, timedelta
import re
import unicodedata
from typing import Iterable

from app.models import Odd


_ALIASES = {
    "1": "home",
    "home": "home",
    "casa": "home",
    "mandante": "home",
    "2": "away",
    "away": "away",
    "fora": "away",
    "visitante": "away",
    "x": "draw",
    "draw": "draw",
    "empate": "draw",
    "yes": "yes",
    "sim": "yes",
    "no": "no",
    "nao": "no",
}


def canonical_selection(value: str) -> str:
    """Normaliza seleções equivalentes sem apagar linhas numéricas."""
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    normalized = "".join(
        character for character in normalized
        if not unicodedata.combining(character)
    ).casefold()
    normalized = normalized.replace(",", ".")
    normalized = re.sub(r"\bmais de\b", "over", normalized)
    normalized = re.sub(r"\bmenos de\b", "under", normalized)
    normalized = re.sub(r"\bacima de\b", "over", normalized)
    normalized = re.sub(r"\babaixo de\b", "under", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return _ALIASES.get(normalized, normalized)


def best_matching_odd(
    odds: Iterable[Odd],
    selection: str,
    *,
    now: datetime,
    maximum_age_hours: float,
) -> Odd | None:
    """Retorna a melhor cotação atual entre seleções semanticamente iguais."""
    target = canonical_selection(selection)
    cutoff = now - timedelta(hours=maximum_age_hours)
    candidates = [
        odd for odd in odds
        if canonical_selection(odd.selection) == target
        and odd.collected_at >= cutoff
        and float(odd.odd_value) > 1
    ]
    return max(
        candidates,
        key=lambda odd: (float(odd.odd_value), odd.collected_at),
        default=None,
    )
