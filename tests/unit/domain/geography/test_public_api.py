"""Testes da API pública do domínio geográfico."""

from ultrastats_ai.domain.geography import (
    AliasNotFoundError,
    Aliases,
    DuplicateAliasError,
    GeographyDomainError,
)
from ultrastats_ai.domain.geography.aliases import (
    Aliases as InternalAliases,
)
from ultrastats_ai.domain.geography.errors import (
    AliasNotFoundError as InternalAliasNotFoundError,
)
from ultrastats_ai.domain.geography.errors import (
    DuplicateAliasError as InternalDuplicateAliasError,
)
from ultrastats_ai.domain.geography.errors import (
    GeographyDomainError as InternalGeographyDomainError,
)


def test_geography_types_are_exported_by_public_api() -> None:
    assert Aliases is InternalAliases
    assert AliasNotFoundError is InternalAliasNotFoundError
    assert DuplicateAliasError is InternalDuplicateAliasError
    assert GeographyDomainError is InternalGeographyDomainError