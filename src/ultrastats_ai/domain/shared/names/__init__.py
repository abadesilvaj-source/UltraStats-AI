"""Biblioteca compartilhada de nomes canônicos do domínio."""

from ultrastats_ai.domain.shared.names.base import (
    DisplayName,
    Name,
    ProperName,
    ShortName,
)
from ultrastats_ai.domain.shared.names.geography import (
    CityName,
    CountryName,
    RegionName,
)

__all__ = [
    "CityName",
    "CountryName",
    "DisplayName",
    "Name",
    "ProperName",
    "RegionName",
    "ShortName",
]