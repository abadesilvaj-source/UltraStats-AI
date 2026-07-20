"""Value Object para nomes de regiões administrativas."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.names.base.proper_name import ProperName


@dataclass(frozen=True, slots=True)
class RegionName(ProperName):
    """Nome oficial de uma região administrativa."""