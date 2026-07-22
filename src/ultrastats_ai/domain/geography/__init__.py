"""API pública do domínio geográfico."""

from ultrastats_ai.domain.geography.aliases import Aliases
from ultrastats_ai.domain.geography.errors import (
    AliasNotFoundError,
    DuplicateAliasError,
    GeographyDomainError,
)

__all__ = [
    "AliasNotFoundError",
    "Aliases",
    "DuplicateAliasError",
    "GeographyDomainError",
]