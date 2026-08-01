"""Value Object para nomes de regiões administrativas."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.names.geography.geographic_name import (
    GeographicName,
)


@dataclass(frozen=True, slots=True)
class RegionName(GeographicName):
    """Nome oficial de uma região administrativa."""