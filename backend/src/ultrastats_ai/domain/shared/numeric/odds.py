"""Value Object para odds decimais."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.decimal_value import DecimalValue


@dataclass(frozen=True, slots=True)
class Odds(DecimalValue):
    """Representa uma odd decimal maior que 1."""

    def _validate(self) -> None:
        if self.value <= Decimal("1"):
            raise DomainValidationError(
                "Odds deve ser maior que 1."
            )

    @property
    def implied_probability(self) -> Decimal:
        """Retorna a probabilidade implícita da odd."""
        return Decimal("1") / self.value