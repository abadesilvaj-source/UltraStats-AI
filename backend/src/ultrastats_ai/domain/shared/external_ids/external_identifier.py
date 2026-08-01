"""Identificador textual fornecido por um sistema externo."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import ClassVar

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.text_value import TextValue


@dataclass(frozen=True, slots=True)
class ExternalIdentifier(TextValue):
    """Representa uma chave opaca pertencente a um provider externo."""

    MAX_LENGTH: ClassVar[int] = 128

    def __post_init__(self) -> None:
        """Normaliza e valida o identificador externo."""
        normalized = self._normalize(self.value)

        object.__setattr__(self, "value", normalized)

        TextValue.__post_init__(self)

        if any(character.isspace() for character in self.value):
            raise DomainValidationError(
                "ExternalIdentifier não pode possuir espaços internos."
            )

        if not self.value.isprintable():
            raise DomainValidationError(
                "ExternalIdentifier não pode possuir caracteres de controle."
            )

    @staticmethod
    def _normalize(value: str) -> str:
        """Remove espaços externos sem alterar a chave do provider."""
        if not isinstance(value, str):
            raise TypeError(
                "ExternalIdentifier deve ser criado a partir de uma string."
            )

        normalized_unicode = unicodedata.normalize("NFC", value)

        return normalized_unicode.strip()