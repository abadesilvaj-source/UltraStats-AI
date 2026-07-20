"""Value Object para nomes de países."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.names.geography.geographic_name import (
    GeographicName,
)


@dataclass(frozen=True, slots=True)
class CountryName(GeographicName):
    """Nome oficial de um país."""