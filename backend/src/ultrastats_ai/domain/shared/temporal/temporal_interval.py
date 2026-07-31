"""Value Object para intervalos temporais."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.temporal.utc_timestamp import UtcTimestamp


@dataclass(frozen=True, slots=True)
class TemporalInterval:
    """Representa um intervalo fechado no início e aberto no fim."""

    start: UtcTimestamp
    end: UtcTimestamp

    def __post_init__(self) -> None:
        """Valida os componentes e a ordem temporal."""
        if not isinstance(self.start, UtcTimestamp):
            raise TypeError(
                "TemporalInterval.start deve ser um UtcTimestamp."
            )

        if not isinstance(self.end, UtcTimestamp):
            raise TypeError(
                "TemporalInterval.end deve ser um UtcTimestamp."
            )

        if self.start.value >= self.end.value:
            raise DomainValidationError(
                "TemporalInterval exige start anterior a end."
            )

    @property
    def duration(self) -> timedelta:
        """Retorna a duração total do intervalo."""
        return self.end.value - self.start.value

    @property
    def duration_seconds(self) -> float:
        """Retorna a duração total em segundos."""
        return self.duration.total_seconds()

    def contains(self, timestamp: UtcTimestamp) -> bool:
        """Verifica se o timestamp pertence ao intervalo [start, end)."""
        if not isinstance(timestamp, UtcTimestamp):
            raise TypeError(
                "TemporalInterval.contains exige um UtcTimestamp."
            )

        return self.start.value <= timestamp.value < self.end.value

    def overlaps(self, other: TemporalInterval) -> bool:
        """Verifica se dois intervalos possuem interseção."""
        if not isinstance(other, TemporalInterval):
            raise TypeError(
                "TemporalInterval.overlaps exige outro TemporalInterval."
            )

        return (
            self.start.value < other.end.value
            and other.start.value < self.end.value
        )