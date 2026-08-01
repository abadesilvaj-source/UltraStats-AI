"""Value Object para peso em quilogramas."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.decimal_value import DecimalValue


@dataclass(frozen=True, slots=True)
class Weight(DecimalValue):
    """Representa um peso em quilogramas."""

    def _validate(self) -> None:
        if not Decimal("0") < self.value <= Decimal("500"):
            raise DomainValidationError(
                "Weight deve estar acima de 0 e até 500 quilogramas."
            )