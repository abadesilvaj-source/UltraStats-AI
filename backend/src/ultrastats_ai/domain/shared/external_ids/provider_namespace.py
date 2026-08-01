"""Namespace canônico utilizado para identificar providers externos."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.text_value import TextValue


@dataclass(frozen=True, slots=True)
class ProviderNamespace(TextValue):
    """Representa o namespace estável de um provider externo."""

    MAX_LENGTH: ClassVar[int] = 64

    _VALID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$"
    )

    def __post_init__(self) -> None:
        """Normaliza e valida o namespace do provider."""
        normalized = self._normalize(self.value)

        object.__setattr__(self, "value", normalized)

        TextValue.__post_init__(self)

        if not self._VALID_PATTERN.fullmatch(self.value):
            raise DomainValidationError(
                "ProviderNamespace aceita apenas letras minúsculas, números, "
                "ponto, hífen e underscore entre segmentos."
            )

    @staticmethod
    def _normalize(value: str) -> str:
        """Converte o namespace para sua forma canônica."""
        if not isinstance(value, str):
            raise TypeError(
                "ProviderNamespace deve ser criado a partir de uma string."
            )

        stripped = value.strip()
        lowered = stripped.lower()

        return re.sub(r"\s+", "_", lowered)