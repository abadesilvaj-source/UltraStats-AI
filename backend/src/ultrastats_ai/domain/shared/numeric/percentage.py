"""Value Object para porcentagens."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.decimal_value import DecimalValue


@dataclass(frozen=True, slots=True)
class Percentage(DecimalValue):
    """Representa uma porcentagem entre 0 e 100."""

    def _validate(self) -> None:
        if not Decimal("0") <= self.value <= Decimal("100"):
            raise DomainValidationError(
                "Percentage deve estar entre 0 e 100."
            )