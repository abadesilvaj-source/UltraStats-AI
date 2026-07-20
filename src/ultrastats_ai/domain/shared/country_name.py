"""Value Object para nomes de países."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.proper_name import ProperName


@dataclass(frozen=True, slots=True)
class CountryName(ProperName):
    """Nome oficial de um país."""