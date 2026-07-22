"""API pública do domínio geográfico."""

from ultrastats_ai.domain.geography.aliases import Aliases
from ultrastats_ai.domain.geography.city import City
from ultrastats_ai.domain.geography.country import Country
from ultrastats_ai.domain.geography.errors import (
    AliasNotFoundError,
    CityNameAliasConflictError,
    CountryNameAliasConflictError,
    DuplicateAliasError,
    GeographyDomainError,
    RegionNameAliasConflictError,
    StadiumNameAliasConflictError,
)
from ultrastats_ai.domain.geography.region import Region
from ultrastats_ai.domain.geography.stadium import Stadium

__all__ = [
    "AliasNotFoundError",
    "Aliases",
    "City",
    "CityNameAliasConflictError",
    "Country",
    "CountryNameAliasConflictError",
    "DuplicateAliasError",
    "GeographyDomainError",
    "Region",
    "RegionNameAliasConflictError",
    "Stadium",
    "StadiumNameAliasConflictError",
]