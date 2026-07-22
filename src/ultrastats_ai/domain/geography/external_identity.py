"""Mapeamentos de identidades externas do domínio geográfico."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from ultrastats_ai.domain.geography.errors import (
    DuplicateExternalIdentityError,
    ExternalIdentityNotFoundError,
)
from ultrastats_ai.domain.geography.history import (
    GeographyEntityKind,
)
from ultrastats_ai.domain.shared import (
    CanonicalId,
    ExternalIdentity,
    ProviderNamespace,
)


@dataclass(frozen=True, slots=True)
class GeographyExternalIdentityMapping:
    """Relaciona uma identidade externa a uma entidade canônica."""

    entity_id: CanonicalId
    entity_kind: GeographyEntityKind
    external_identity: ExternalIdentity

    def __post_init__(self) -> None:
        """Valida os componentes do mapeamento."""
        if not isinstance(self.entity_id, CanonicalId):
            raise TypeError(
                "entity_id deve ser uma instância de CanonicalId."
            )

        if not isinstance(
            self.entity_kind,
            GeographyEntityKind,
        ):
            raise TypeError(
                "entity_kind deve ser uma instância de "
                "GeographyEntityKind."
            )

        if not isinstance(
            self.external_identity,
            ExternalIdentity,
        ):
            raise TypeError(
                "external_identity deve ser uma instância de "
                "ExternalIdentity."
            )

    @property
    def provider(self) -> ProviderNamespace:
        """Retorna o namespace do provider externo."""
        return self.external_identity.provider

    @property
    def key(self) -> str:
        """Retorna a chave textual da identidade externa."""
        return self.external_identity.key

    def belongs_to(
        self,
        entity_id: CanonicalId,
        entity_kind: GeographyEntityKind | None = None,
    ) -> bool:
        """Verifica se o mapeamento pertence à entidade informada."""
        if not isinstance(entity_id, CanonicalId):
            return False

        if entity_kind is not None and not isinstance(
            entity_kind,
            GeographyEntityKind,
        ):
            return False

        if self.entity_id != entity_id:
            return False

        if entity_kind is None:
            return True

        return self.entity_kind is entity_kind

    def is_from_provider(
        self,
        provider: ProviderNamespace,
    ) -> bool:
        """Verifica se o mapeamento pertence ao provider informado."""
        if not isinstance(provider, ProviderNamespace):
            return False

        return self.provider == provider


@dataclass(frozen=True, slots=True)
class GeographyExternalIdentities:
    """Coleção imutável de identidades externas geográficas."""

    _items: tuple[GeographyExternalIdentityMapping, ...] = ()

    def __post_init__(self) -> None:
        """Valida os itens e impede identidades duplicadas."""
        if not isinstance(self._items, tuple):
            raise TypeError(
                "_items deve ser uma tuple."
            )

        known_external_identities: set[ExternalIdentity] = set()

        for item in self._items:
            if not isinstance(
                item,
                GeographyExternalIdentityMapping,
            ):
                raise TypeError(
                    "_items deve conter somente instâncias de "
                    "GeographyExternalIdentityMapping."
                )

            if (
                item.external_identity
                in known_external_identities
            ):
                raise DuplicateExternalIdentityError(
                    "A identidade externa já está vinculada a "
                    "uma entidade geográfica."
                )

            known_external_identities.add(
                item.external_identity
            )

    @classmethod
    def empty(cls) -> GeographyExternalIdentities:
        """Cria uma coleção vazia."""
        return cls()

    @classmethod
    def from_iterable(
        cls,
        values: Iterable[
            GeographyExternalIdentityMapping
        ],
    ) -> GeographyExternalIdentities:
        """Cria a coleção a partir de qualquer iterável."""
        if isinstance(values, (str, bytes)):
            raise TypeError(
                "values deve ser um iterável de "
                "GeographyExternalIdentityMapping."
            )

        try:
            items = tuple(values)
        except TypeError as error:
            raise TypeError(
                "values deve ser um iterável de "
                "GeographyExternalIdentityMapping."
            ) from error

        return cls(items)

    def add(
        self,
        mapping: GeographyExternalIdentityMapping,
    ) -> GeographyExternalIdentities:
        """Retorna uma nova coleção contendo o mapeamento."""
        if not isinstance(
            mapping,
            GeographyExternalIdentityMapping,
        ):
            raise TypeError(
                "mapping deve ser uma instância de "
                "GeographyExternalIdentityMapping."
            )

        if self.contains(mapping.external_identity):
            raise DuplicateExternalIdentityError(
                "A identidade externa já está vinculada a "
                "uma entidade geográfica."
            )

        return GeographyExternalIdentities(
            self._items + (mapping,)
        )

    def discard(
        self,
        external_identity: ExternalIdentity,
    ) -> GeographyExternalIdentities:
        """Retorna uma coleção sem a identidade informada."""
        if not isinstance(
            external_identity,
            ExternalIdentity,
        ):
            raise TypeError(
                "external_identity deve ser uma instância de "
                "ExternalIdentity."
            )

        if not self.contains(external_identity):
            raise ExternalIdentityNotFoundError(
                "A identidade externa informada não foi encontrada."
            )

        return GeographyExternalIdentities(
            tuple(
                item
                for item in self._items
                if item.external_identity != external_identity
            )
        )

    def contains(
        self,
        external_identity: ExternalIdentity,
    ) -> bool:
        """Verifica se a identidade externa está na coleção."""
        if not isinstance(
            external_identity,
            ExternalIdentity,
        ):
            return False

        return any(
            item.external_identity == external_identity
            for item in self._items
        )

    def get(
        self,
        external_identity: ExternalIdentity,
    ) -> GeographyExternalIdentityMapping | None:
        """Retorna o mapeamento da identidade externa."""
        if not isinstance(
            external_identity,
            ExternalIdentity,
        ):
            return None

        for item in self._items:
            if item.external_identity == external_identity:
                return item

        return None

    def find_by_provider(
        self,
        provider: ProviderNamespace,
    ) -> tuple[GeographyExternalIdentityMapping, ...]:
        """Retorna os mapeamentos pertencentes ao provider."""
        if not isinstance(provider, ProviderNamespace):
            raise TypeError(
                "provider deve ser uma instância de "
                "ProviderNamespace."
            )

        return tuple(
            item
            for item in self._items
            if item.is_from_provider(provider)
        )

    def find_by_entity(
        self,
        entity_id: CanonicalId,
        entity_kind: GeographyEntityKind | None = None,
    ) -> tuple[GeographyExternalIdentityMapping, ...]:
        """Retorna os mapeamentos de uma entidade canônica."""
        if not isinstance(entity_id, CanonicalId):
            raise TypeError(
                "entity_id deve ser uma instância de CanonicalId."
            )

        if entity_kind is not None and not isinstance(
            entity_kind,
            GeographyEntityKind,
        ):
            raise TypeError(
                "entity_kind deve ser uma instância de "
                "GeographyEntityKind ou None."
            )

        return tuple(
            item
            for item in self._items
            if item.belongs_to(entity_id, entity_kind)
        )

    def __iter__(
        self,
    ) -> Iterator[GeographyExternalIdentityMapping]:
        """Permite iterar sobre os mapeamentos."""
        return iter(self._items)

    def __len__(self) -> int:
        """Retorna o número de mapeamentos."""
        return len(self._items)

    def __bool__(self) -> bool:
        """Informa se a coleção contém mapeamentos."""
        return bool(self._items)