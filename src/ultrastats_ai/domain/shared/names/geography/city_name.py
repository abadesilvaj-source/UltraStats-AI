"""Value Object para nomes de cidades."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.names.base.proper_name import ProperName


@dataclass(frozen=True, slots=True)
class CityName(ProperName):
    """Nome oficial de uma cidade."""