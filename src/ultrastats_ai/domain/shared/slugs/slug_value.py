"""Value Object textual utilizado para representar slugs canônicos."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import ClassVar

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.text_value import TextValue


@dataclass(frozen=True, slots=True)
class SlugValue(TextValue):
    """Representa um identificador textual apropriado para URLs."""

    MAX_LENGTH: ClassVar[int] = 128

    _VALID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    )

    def __post_init__(self) -> None:
        """Normaliza e valida o valor textual do slug."""
        normalized = self._normalize(self.value)

        object.__setattr__(self, "value", normalized)

        TextValue.__post_init__(self)

        if not self._VALID_PATTERN.fullmatch(self.value):
            raise DomainValidationError(
                "SlugValue aceita apenas letras minúsculas de a a z, "
                "números e hífens simples entre palavras."
            )

    @staticmethod
    def _normalize(value: str) -> str:
        """Converte um texto válido para o formato canônico de slug."""
        if not isinstance(value, str):
            raise TypeError("SlugValue deve ser criado a partir de uma string.")

        stripped = value.strip()
        lowered = stripped.lower()

        decomposed = unicodedata.normalize("NFKD", lowered)

        without_accents = "".join(
            character
            for character in decomposed
            if not unicodedata.combining(character)
        )

        return re.sub(r"\s+", "-", without_accents)