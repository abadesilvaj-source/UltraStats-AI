"""Value Objects compartilhados para nomes canônicos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.text_value import TextValue


@dataclass(frozen=True, slots=True)
class Name(TextValue):
    """Nome canônico compartilhado pelo domínio.

    A classe aceita caracteres Unicode e símbolos normalmente presentes em
    nomes reais, como:

    - acentos;
    - hífens;
    - apóstrofos;
    - pontos;
    - números;
    - caracteres de diferentes alfabetos.

    Ao menos um caractere alfanumérico deve estar presente.
    """

    MIN_LENGTH: ClassVar[int] = 2
    MAX_LENGTH: ClassVar[int] = 150

    def validate_specific_rules(self) -> None:
        """Valida regras semânticas básicas para nomes."""

        if not any(character.isalnum() for character in self.value):
            raise DomainValidationError(
                f"{type(self).__name__} deve possuir pelo menos "
                "um caractere alfanumérico."
            )