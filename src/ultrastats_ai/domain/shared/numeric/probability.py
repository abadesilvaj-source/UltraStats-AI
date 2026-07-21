"""Value Object para probabilidades."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.decimal_value import DecimalValue


@dataclass(frozen=True, slots=True)
class Probability(DecimalValue):
    """Representa uma probabilidade entre 0 e 1."""

    def _validate(self) -> None:
        if not Decimal("0") <= self.value <= Decimal("1"):
            raise DomainValidationError(
                "Probability deve estar entre 0 e 1."
            )