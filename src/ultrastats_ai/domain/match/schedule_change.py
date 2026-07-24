"""Histórico imutável de alterações da agenda de uma partida."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.match.errors import InvalidScheduleChangeError
from ultrastats_ai.domain.shared import (
    DomainDate,
    MatchId,
    MatchScheduleChangeId,
    UtcTimestamp,
)


@dataclass(frozen=True, slots=True)
class MatchScheduleChange:
    """Registra uma mudança de data ou horário sem trocar o MatchId."""

    id: MatchScheduleChangeId
    match_id: MatchId
    changed_at: UtcTimestamp
    reason: str
    previous_date: DomainDate | None = None
    previous_start_at: UtcTimestamp | None = None
    new_date: DomainDate | None = None
    new_start_at: UtcTimestamp | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, MatchScheduleChangeId):
            raise TypeError("id deve ser MatchScheduleChangeId.")
        if not isinstance(self.match_id, MatchId):
            raise TypeError("match_id deve ser MatchId.")
        if not isinstance(self.changed_at, UtcTimestamp):
            raise TypeError("changed_at deve ser UtcTimestamp.")
        if not isinstance(self.reason, str):
            raise TypeError("reason deve ser str.")
        for field_name, value, expected_type in (
            ("previous_date", self.previous_date, DomainDate),
            ("previous_start_at", self.previous_start_at, UtcTimestamp),
            ("new_date", self.new_date, DomainDate),
            ("new_start_at", self.new_start_at, UtcTimestamp),
        ):
            if value is not None and not isinstance(value, expected_type):
                raise TypeError(
                    f"{field_name} possui tipo inválido."
                )

        normalized_reason = self.reason.strip()
        if not normalized_reason:
            raise InvalidScheduleChangeError(
                "A alteração de agenda exige um motivo."
            )
        if self.new_date is None and self.new_start_at is None:
            raise InvalidScheduleChangeError(
                "A nova agenda exige data ou horário."
            )
        if (
            self.previous_date == self.new_date
            and self.previous_start_at == self.new_start_at
        ):
            raise InvalidScheduleChangeError(
                "A nova agenda deve ser diferente da anterior."
            )

        object.__setattr__(self, "reason", normalized_reason)
