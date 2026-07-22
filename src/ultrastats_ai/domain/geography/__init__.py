"""API pública do domínio geográfico."""

from ultrastats_ai.domain.geography.aliases import Aliases
from ultrastats_ai.domain.geography.city import City
from ultrastats_ai.domain.geography.country import Country
from ultrastats_ai.domain.geography.errors import (
    AliasNotFoundError,
    CityNameAliasConflictError,
    CountryNameAliasConflictError,
    DuplicateAliasError,
    DuplicateExternalIdentityError,
    DuplicateHistoryFieldError,
    EmptyHistoryChangesError,
    ExternalIdentityNotFoundError,
    GeographyDomainError,
    GeographyExternalIdentityError,
    GeographyHistoryError,
    RegionNameAliasConflictError,
    StadiumNameAliasConflictError,
)
from ultrastats_ai.domain.geography.external_identity import (
    GeographyExternalIdentities,
    GeographyExternalIdentityMapping,
)
from ultrastats_ai.domain.geography.history import (
    GeographyChangeType,
    GeographyEntityKind,
    GeographyFieldChange,
    GeographyHistoryEntry,
)
from ultrastats_ai.domain.geography.reconstruction import (
    CityReconstruction,
    CountryReconstruction,
    RegionReconstruction,
    StadiumReconstruction,
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
    "CityReconstruction",
    "CityRepository",
    "Country",
    "CountryNameAliasConflictError",
    "CountryReconstruction",
    "CountryRepository",
    "DuplicateAliasError",
    "DuplicateExternalIdentityError",
    "DuplicateHistoryFieldError",
    "EmptyHistoryChangesError",
    "ExternalIdentityNotFoundError",
    "GeographyChangeType",
    "GeographyDomainError",
    "GeographyEntityKind",
    "GeographyExternalIdentities",
    "GeographyExternalIdentityError",
    "GeographyExternalIdentityMapping",
    "GeographyFieldChange",
    "GeographyHistoryEntry",
    "GeographyHistoryError",
    "GeographyHistoryRepository",
    "Region",
    "RegionNameAliasConflictError",
    "RegionReconstruction",
    "RegionRepository",
    "Stadium",
    "StadiumNameAliasConflictError",
    "StadiumReconstruction",
    "StadiumRepository",
]