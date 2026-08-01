"""Value Object para nomes de locais esportivos."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.names.geography.geographic_name import (
    GeographicName,
)


@dataclass(frozen=True, slots=True)
class VenueName(GeographicName):
    """Nome canônico de um estádio, arena ou outro local esportivo."""