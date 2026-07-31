"""Value Object para idade."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.integer_value import IntegerValue


@dataclass(frozen=True, slots=True)
class Age(IntegerValue):
    """Representa uma idade entre 0 e 130 anos."""

    def _validate(self) -> None:
        if not 0 <= self.value <= 130:
            raise DomainValidationError(
                "Age deve estar entre 0 e 130."
            )