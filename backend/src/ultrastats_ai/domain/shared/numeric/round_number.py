"""Value Object para números de rodada."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.integer_value import IntegerValue


@dataclass(frozen=True, slots=True)
class RoundNumber(IntegerValue):
    """Representa o número positivo de uma rodada."""

    def _validate(self) -> None:
        if self.value < 1:
            raise DomainValidationError(
                "RoundNumber deve ser maior ou igual a 1."
            )