"""Value Object para altura em centímetros."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.decimal_value import DecimalValue


@dataclass(frozen=True, slots=True)
class Height(DecimalValue):
    """Representa uma altura em centímetros."""

    def _validate(self) -> None:
        if not Decimal("0") < self.value <= Decimal("300"):
            raise DomainValidationError(
                "Height deve estar acima de 0 e até 300 centímetros."
            )

    @property
    def meters(self) -> Decimal:
        """Retorna a altura convertida para metros."""
        return self.value / Decimal("100")