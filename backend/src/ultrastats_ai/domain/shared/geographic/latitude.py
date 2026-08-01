"""Value Object para latitude geográfica."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.decimal_value import DecimalValue


@dataclass(frozen=True, slots=True)
class Latitude(DecimalValue):
    """Representa uma latitude entre -90 e 90 graus."""

    def _validate(self) -> None:
        if not Decimal("-90") <= self.value <= Decimal("90"):
            raise DomainValidationError(
                "Latitude deve estar entre -90 e 90 graus."
            )