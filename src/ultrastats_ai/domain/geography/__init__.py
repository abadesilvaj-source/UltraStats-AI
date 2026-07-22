"""API pública do domínio geográfico."""

from ultrastats_ai.domain.geography.aliases import Aliases
from ultrastats_ai.domain.geography.city import City
from ultrastats_ai.domain.geography.country import Country
from ultrastats_ai.domain.geography.errors import (
    AliasNotFoundError,
    CityNameAliasConflictError,
    CountryNameAliasConflictError,
    DuplicateAliasError,
    DuplicateHistoryFieldError,
    EmptyHistoryChangesError,
    GeographyDomainError,
    GeographyHistoryError,
    RegionNameAliasConflictError,
    StadiumNameAliasConflictError,
)
from ultrastats_ai.domain.geography.history import (
    GeographyChangeType,
    GeographyEntityKind,
    GeographyFieldChange,
    GeographyHistoryEntry,
)
from ultrastats_ai.domain.geography.region import Region
from ultrastats_ai.domain.geography.repositories import (
    CityRepository,
    CountryRepository,
    GeographyHistoryRepository,
    RegionRepository,
    StadiumRepository,
)
from ultrastats_ai.domain.geography.stadium import Stadium

__all__ = [
    "AliasNotFoundError",
    "Aliases",
    "City",
    "CityNameAliasConflictError",
    "CityRepository",
    "Country",
    "CountryNameAliasConflictError",
    "CountryRepository",
    "DuplicateAliasError",
    "DuplicateHistoryFieldError",
    "EmptyHistoryChangesError",
    "GeographyChangeType",
    "GeographyDomainError",
    "GeographyEntityKind",
    "GeographyFieldChange",
    "GeographyHistoryEntry",
    "GeographyHistoryError",
    "GeographyHistoryRepository",
    "Region",
    "RegionNameAliasConflictError",
    "RegionRepository",
    "Stadium",
    "StadiumNameAliasConflictError",
    "StadiumRepository",
]