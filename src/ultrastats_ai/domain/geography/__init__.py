"""API pública do domínio geográfico."""

from ultrastats_ai.domain.geography.aliases import Aliases
from ultrastats_ai.domain.geography.country import Country
from ultrastats_ai.domain.geography.errors import (
    AliasNotFoundError,
    CountryNameAliasConflictError,
    DuplicateAliasError,
    GeographyDomainError,
)

__all__ = [
    "AliasNotFoundError",
    "Aliases",
    "Country",
    "CountryNameAliasConflictError",
    "DuplicateAliasError",
    "GeographyDomainError",
]