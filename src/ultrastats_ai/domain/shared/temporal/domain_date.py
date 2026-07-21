"""Value Object para datas do domínio sem horário."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from ultrastats_ai.domain.shared.errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class DomainDate:
    """Representa uma data do calendário sem horário ou timezone."""

    value: date | str

    def __post_init__(self) -> None:
        """Normaliza a entrada para um objeto date."""
        normalized = self._normalize(self.value)

        object.__setattr__(self, "value", normalized)

    @classmethod
    def _normalize(cls, value: date | str) -> date:
        """Converte uma data ou string ISO para date."""
        if isinstance(value, datetime):
            raise TypeError(
                "DomainDate não aceita datetime; utilize apenas date "
                "ou uma string no formato YYYY-MM-DD."
            )

        if isinstance(value, date):
            return value

        if isinstance(value, str):
            stripped = value.strip()

            if not stripped:
                raise DomainValidationError(
                    "DomainDate não pode ser vazio."
                )

            try:
                return date.fromisoformat(stripped)
            except ValueError:
                raise DomainValidationError(
                    "DomainDate deve possuir o formato válido YYYY-MM-DD."
                ) from None

        raise TypeError(
            "DomainDate deve receber date ou str."
        )

    @property
    def isoformat(self) -> str:
        """Retorna a data no formato ISO YYYY-MM-DD."""
        return self.value.isoformat()

    def add_days(self, days: int) -> DomainDate:
        """Retorna uma nova data com a quantidade indicada de dias."""
        if isinstance(days, bool) or not isinstance(days, int):
            raise TypeError(
                "DomainDate.add_days deve receber um número inteiro."
            )

        return DomainDate(self.value + timedelta(days=days))

    def days_until(self, other: DomainDate) -> int:
        """Retorna a diferença em dias até outra data."""
        if not isinstance(other, DomainDate):
            raise TypeError(
                "DomainDate.days_until exige outro DomainDate."
            )

        return (other.value - self.value).days