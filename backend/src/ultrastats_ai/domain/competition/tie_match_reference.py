"""Referência de Tie para Match."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared import MatchId


@dataclass(frozen=True, slots=True)
class TieMatchReference:
    """Representa uma partida pertencente a um confronto."""

    match_id: MatchId
    sequence: int

    def __post_init__(self) -> None:
        if not isinstance(self.match_id, MatchId):
            raise TypeError("match_id deve ser MatchId.")

        if (
            isinstance(self.sequence, bool)
            or not isinstance(self.sequence, int)
        ):
            raise TypeError("sequence deve ser int.")

        if self.sequence < 1:
            raise ValueError(
                "sequence deve ser maior ou igual a 1."
            )