"""Objetos de domínio relacionados ao histórico geográfico."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from ultrastats_ai.domain.geography.errors import (
    DuplicateHistoryFieldError,
    EmptyHistoryChangesError,
)
from ultrastats_ai.domain.shared import (
    CanonicalId,
    UtcTimestamp,
)


class GeographyEntityKind(str, Enum):
    """Tipos de entidades geográficas reconhecidas pelo domínio."""

    COUNTRY = "country"
    REGION = "region"
    CITY = "city"
    STADIUM = "stadium"

    def __str__(self) -> str:
        """Retorna o valor canônico textual."""
        return self.value

    @classmethod
    def parse(cls, value: str) -> GeographyEntityKind:
        """Converte um texto em um tipo de entidade geográfica."""
        if not isinstance(value, str):
            raise TypeError(
                "value deve ser uma string."
            )

        normalized = value.strip().lower().replace("-", "_").replace(
            " ",
            "_",
        )

        for member in cls:
            if member.value == normalized:
                return member

        raise ValueError(
            f"Tipo de entidade geográfica desconhecido: {value!r}."
        )


class GeographyChangeType(str, Enum):
    """Tipos de alterações registradas no histórico geográfico."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"

    def __str__(self) -> str:
        """Retorna o valor canônico textual."""
        return self.value

    @classmethod
    def parse(cls, value: str) -> GeographyChangeType:
        """Converte um texto em um tipo de alteração."""
        if not isinstance(value, str):
            raise TypeError(
                "value deve ser uma string."
            )

        normalized = value.strip().lower().replace("-", "_").replace(
            " ",
            "_",
        )

        for member in cls:
            if member.value == normalized:
                return member

        raise ValueError(
            f"Tipo de alteração geográfica desconhecido: {value!r}."
        )


@dataclass(frozen=True, slots=True)
class GeographyFieldChange:
    """Representa a alteração de um campo de entidade geográfica."""

    field_name: str
    previous_value: str | None
    current_value: str | None

    def __post_init__(self) -> None:
        """Valida e normaliza os dados da alteração."""
        if not isinstance(self.field_name, str):
            raise TypeError(
                "field_name deve ser uma string."
            )

        normalized_field_name = self.field_name.strip()

        if not normalized_field_name:
            raise ValueError(
                "field_name não pode ser vazio."
            )

        if (
            self.previous_value is not None
            and not isinstance(self.previous_value, str)
        ):
            raise TypeError(
                "previous_value deve ser uma string ou None."
            )

        if (
            self.current_value is not None
            and not isinstance(self.current_value, str)
        ):
            raise TypeError(
                "current_value deve ser uma string ou None."
            )

        normalized_previous = (
            self.previous_value.strip()
            if self.previous_value is not None
            else None
        )

        normalized_current = (
            self.current_value.strip()
            if self.current_value is not None
            else None
        )

        if normalized_previous == normalized_current:
            raise ValueError(
                "previous_value e current_value devem ser diferentes."
            )

        object.__setattr__(
            self,
            "field_name",
            normalized_field_name,
        )
        object.__setattr__(
            self,
            "previous_value",
            normalized_previous,
        )
        object.__setattr__(
            self,
            "current_value",
            normalized_current,
        )

    @property
    def is_creation(self) -> bool:
        """Informa se o campo foi criado."""
        return (
            self.previous_value is None
            and self.current_value is not None
        )

    @property
    def is_removal(self) -> bool:
        """Informa se o campo foi removido."""
        return (
            self.previous_value is not None
            and self.current_value is None
        )

    @property
    def is_update(self) -> bool:
        """Informa se o campo foi alterado."""
        return (
            self.previous_value is not None
            and self.current_value is not None
        )


@dataclass(frozen=True, slots=True)
class GeographyHistoryEntry:
    """Representa uma entrada imutável do histórico geográfico."""

    id: CanonicalId
    entity_id: CanonicalId
    entity_kind: GeographyEntityKind
    change_type: GeographyChangeType
    occurred_at: UtcTimestamp
    changes: tuple[GeographyFieldChange, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        """Valida os tipos e invariantes da entrada de histórico."""
        if not isinstance(self.id, CanonicalId):
            raise TypeError(
                "id deve ser uma instância de CanonicalId."
            )

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
            self.change_type,
            GeographyChangeType,
        ):
            raise TypeError(
                "change_type deve ser uma instância de "
                "GeographyChangeType."
            )

        if not isinstance(self.occurred_at, UtcTimestamp):
            raise TypeError(
                "occurred_at deve ser uma instância de "
                "UtcTimestamp."
            )

        if not isinstance(self.changes, tuple):
            raise TypeError(
                "changes deve ser uma tuple."
            )

        for change in self.changes:
            if not isinstance(change, GeographyFieldChange):
                raise TypeError(
                    "changes deve conter apenas instâncias de "
                    "GeographyFieldChange."
                )

        self._validate_duplicate_fields()
        self._validate_updated_entry()

    @classmethod
    def from_iterable(
        cls,
        *,
        id: CanonicalId,
        entity_id: CanonicalId,
        entity_kind: GeographyEntityKind,
        change_type: GeographyChangeType,
        occurred_at: UtcTimestamp,
        changes: Iterable[GeographyFieldChange],
    ) -> GeographyHistoryEntry:
        """Cria uma entrada a partir de qualquer iterável de alterações."""
        if isinstance(changes, (str, bytes)):
            raise TypeError(
                "changes deve ser um iterável de "
                "GeographyFieldChange."
            )

        return cls(
            id=id,
            entity_id=entity_id,
            entity_kind=entity_kind,
            change_type=change_type,
            occurred_at=occurred_at,
            changes=tuple(changes),
        )

    def _validate_duplicate_fields(self) -> None:
        """Impede o registro duplicado do mesmo campo."""
        field_names: set[str] = set()

        for change in self.changes:
            normalized_name = change.field_name.casefold()

            if normalized_name in field_names:
                raise DuplicateHistoryFieldError(
                    "Um campo não pode aparecer mais de uma vez "
                    "na mesma entrada de histórico."
                )

            field_names.add(normalized_name)

    def _validate_updated_entry(self) -> None:
        """Exige ao menos uma alteração para entradas UPDATED."""
        if (
            self.change_type is GeographyChangeType.UPDATED
            and not self.changes
        ):
            raise EmptyHistoryChangesError(
                "Uma atualização geográfica deve possuir ao "
                "menos uma alteração."
            )

    @property
    def changed_fields(self) -> tuple[str, ...]:
        """Retorna os nomes dos campos alterados."""
        return tuple(
            change.field_name
            for change in self.changes
        )

    def has_changed_field(self, field_name: str) -> bool:
        """Informa se determinado campo foi alterado."""
        if not isinstance(field_name, str):
            return False

        normalized_name = field_name.strip().casefold()

        return any(
            change.field_name.casefold() == normalized_name
            for change in self.changes
        )

    def get_change(
        self,
        field_name: str,
    ) -> GeographyFieldChange | None:
        """Retorna a alteração de um campo, quando existente."""
        if not isinstance(field_name, str):
            return None

        normalized_name = field_name.strip().casefold()

        for change in self.changes:
            if change.field_name.casefold() == normalized_name:
                return change

        return None