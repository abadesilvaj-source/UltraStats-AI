"""Value Object compartilhado para nomes de exibição."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ultrastats_ai.domain.shared.name import Name


@dataclass(frozen=True, slots=True)
class DisplayName(Name):
    """Nome destinado à apresentação em interfaces.

    Um nome de exibição pode ser diferente do nome oficial.

    Exemplos:

    - ``Manchester United Football Club`` como nome oficial;
    - ``Manchester United`` como nome de exibição;
    - ``Paris Saint-Germain Football Club`` como nome oficial;
    - ``Paris Saint-Germain`` como nome de exibição.

    O tipo não representa necessariamente uma abreviação extrema. Para nomes
    muito curtos deverá ser utilizado ``ShortName``.
    """

    MIN_LENGTH: ClassVar[int] = 1
    MAX_LENGTH: ClassVar[int] = 100