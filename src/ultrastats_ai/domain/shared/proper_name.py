"""Value Object compartilhado para nomes oficiais."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ultrastats_ai.domain.shared.name import Name


@dataclass(frozen=True, slots=True)
class ProperName(Name):
    """Nome oficial ou principal de um elemento do domínio.

    Exemplos:

    - nome oficial de um país;
    - nome oficial de uma competição;
    - nome oficial de uma equipe;
    - nome completo de uma pessoa;
    - nome oficial de um estádio;
    - nome oficial de um provider.

    O tipo preserva caracteres Unicode e utiliza a normalização textual
    definida por ``TextValue``.
    """

    MIN_LENGTH: ClassVar[int] = 2
    MAX_LENGTH: ClassVar[int] = 150