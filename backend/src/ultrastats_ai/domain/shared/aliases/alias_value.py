"""Value Object textual utilizado para representar aliases canônicos."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import ClassVar

from ultrastats_ai.domain.shared.text_value import TextValue


@dataclass(frozen=True, slots=True)
class AliasValue(TextValue):
    """Representa uma grafia alternativa associada a uma entidade."""

    MAX_LENGTH: ClassVar[int] = 128

    def __post_init__(self) -> None:
        """Normaliza e valida o alias textual."""
        normalized = self._normalize(self.value)

        object.__setattr__(self, "value", normalized)

        TextValue.__post_init__(self)

    @staticmethod
    def _normalize(value: str) -> str:
        """Normaliza o texto sem apagar sua grafia humana."""
        if not isinstance(value, str):
            raise TypeError("AliasValue deve ser criado a partir de uma string.")

        normalized_unicode = unicodedata.normalize("NFC", value)

        stripped = normalized_unicode.strip()

        return re.sub(r"\s+", " ", stripped)