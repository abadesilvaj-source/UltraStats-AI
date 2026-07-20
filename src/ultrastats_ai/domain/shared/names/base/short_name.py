"""Value Object compartilhado para nomes curtos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ultrastats_ai.domain.shared.names.base.name import Name


@dataclass(frozen=True, slots=True)
class ShortName(Name):
    """Nome curto utilizado em espaços limitados.

    Exemplos:

    - ``Man United``;
    - ``PSG``;
    - ``UCL``;
    - ``Brasileirão``;
    - ``São Paulo``.

    Este tipo não obriga o uso de letras maiúsculas, pois nomes curtos não são
    necessariamente códigos. Códigos serão implementados separadamente durante
    a etapa G5.3.2.3.
    """

    MIN_LENGTH: ClassVar[int] = 1
    MAX_LENGTH: ClassVar[int] = 30