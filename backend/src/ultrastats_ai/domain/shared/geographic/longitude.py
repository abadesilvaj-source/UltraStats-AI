"""Value Object para longitude geográfica."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.decimal_value import DecimalValue


@dataclass(frozen=True, slots=True)
class Longitude(DecimalValue):
    """Representa uma longitude entre -180 e 180 graus."""

    def _validate(self) -> None:
        if not Decimal("-180") <= self.value <= Decimal("180"):
            raise DomainValidationError(
                "Longitude deve estar entre -180 e 180 graus."
            )