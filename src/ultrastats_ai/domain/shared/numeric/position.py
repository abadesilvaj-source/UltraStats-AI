"""Value Object para posições classificatórias."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.integer_value import IntegerValue


@dataclass(frozen=True, slots=True)
class Position(IntegerValue):
    """Representa uma posição positiva em classificação."""

    def _validate(self) -> None:
        if self.value < 1:
            raise DomainValidationError(
                "Position deve ser maior ou igual a 1."
            )