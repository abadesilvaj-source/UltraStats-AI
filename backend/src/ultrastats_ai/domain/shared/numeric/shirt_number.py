"""Value Object para números de camisa."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.integer_value import IntegerValue


@dataclass(frozen=True, slots=True)
class ShirtNumber(IntegerValue):
    """Representa um número de camisa entre 1 e 99."""

    def _validate(self) -> None:
        if not 1 <= self.value <= 99:
            raise DomainValidationError(
                "ShirtNumber deve estar entre 1 e 99."
            )