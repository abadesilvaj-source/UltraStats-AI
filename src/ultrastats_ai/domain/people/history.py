"""Registros imutáveis de histórico do People Context."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Mapping

from ultrastats_ai.domain.people.enums import (
    PeopleHistoryAction,
    PeopleProfileType,
)
from ultrastats_ai.domain.shared import PersonId


@dataclass(frozen=True, slots=True, eq=False)
class PersonHistoryEntry:
    """Representa uma alteração histórica envolvendo uma pessoa."""

    person_id: PersonId
    action: PeopleHistoryAction
    occurred_at: datetime
    profile_type: PeopleProfileType | None = None
    previous_value: str | None = None
    current_value: str | None = None
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.person_id, PersonId):
            raise TypeError("person_id deve ser PersonId.")

        if not isinstance(self.action, PeopleHistoryAction):
            raise TypeError(
                "action deve ser PeopleHistoryAction."
            )

        if not isinstance(self.occurred_at, datetime):
            raise TypeError(
                "occurred_at deve ser datetime."
            )

        if self.occurred_at.tzinfo is None:
            raise ValueError(
                "occurred_at deve possuir timezone."
            )

        if (
            self.occurred_at.utcoffset() is None
        ):
            raise ValueError(
                "occurred_at deve possuir timezone válido."
            )

        if (
            self.profile_type is not None
            and not isinstance(
                self.profile_type,
                PeopleProfileType,
            )
        ):
            raise TypeError(
                "profile_type deve ser PeopleProfileType "
                "ou None."
            )

        self._validate_optional_text(
            self.previous_value,
            "previous_value",
        )
        self._validate_optional_text(
            self.current_value,
            "current_value",
        )

        if (
            self.metadata is not None
            and not isinstance(self.metadata, Mapping)
        ):
            raise TypeError(
                "metadata deve ser Mapping[str, str] ou None."
            )

        normalized_metadata = self._normalize_metadata(
            self.metadata
        )

        object.__setattr__(
            self,
            "occurred_at",
            self.occurred_at.astimezone(timezone.utc),
        )

        object.__setattr__(
            self,
            "metadata",
            normalized_metadata,
        )

    @classmethod
    def create(
        cls,
        *,
        person_id: PersonId,
        action: PeopleHistoryAction,
        occurred_at: datetime,
        profile_type: PeopleProfileType | None = None,
        previous_value: str | None = None,
        current_value: str | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> PersonHistoryEntry:
        """Cria um novo registro histórico validado."""

        return cls(
            person_id=person_id,
            action=action,
            occurred_at=occurred_at,
            profile_type=profile_type,
            previous_value=previous_value,
            current_value=current_value,
            metadata=metadata,
        )

    @classmethod
    def reconstruct(
        cls,
        *,
        person_id: PersonId,
        action: PeopleHistoryAction,
        occurred_at: datetime,
        profile_type: PeopleProfileType | None = None,
        previous_value: str | None = None,
        current_value: str | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> PersonHistoryEntry:
        """Reconstrói um registro histórico persistido."""

        return cls(
            person_id=person_id,
            action=action,
            occurred_at=occurred_at,
            profile_type=profile_type,
            previous_value=previous_value,
            current_value=current_value,
            metadata=metadata,
        )

    @staticmethod
    def _validate_optional_text(
        value: str | None,
        field_name: str,
    ) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError(
                f"{field_name} deve ser str ou None."
            )

        if isinstance(value, str) and not value.strip():
            raise ValueError(
                f"{field_name} não pode ser vazio."
            )

    @staticmethod
    def _normalize_metadata(
        metadata: Mapping[str, str] | None,
    ) -> Mapping[str, str]:
        if metadata is None:
            return MappingProxyType({})

        normalized: dict[str, str] = {}

        for key, value in metadata.items():
            if not isinstance(key, str):
                raise TypeError(
                    "As chaves de metadata devem ser str."
                )

            if not isinstance(value, str):
                raise TypeError(
                    "Os valores de metadata devem ser str."
                )

            normalized_key = key.strip()
            normalized_value = value.strip()

            if not normalized_key:
                raise ValueError(
                    "As chaves de metadata não podem "
                    "ser vazias."
                )

            if not normalized_value:
                raise ValueError(
                    "Os valores de metadata não podem "
                    "ser vazios."
                )

            normalized[normalized_key] = normalized_value

        return MappingProxyType(normalized)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PersonHistoryEntry):
            return NotImplemented

        return (
            self.person_id == other.person_id
            and self.action is other.action
            and self.occurred_at == other.occurred_at
            and self.profile_type is other.profile_type
            and self.previous_value == other.previous_value
            and self.current_value == other.current_value
            and dict(self.metadata or {})
            == dict(other.metadata or {})
        )

    def __hash__(self) -> int:
        metadata_items = tuple(
            sorted(
                dict(self.metadata or {}).items()
            )
        )

        return hash(
            (
                self.person_id,
                self.action,
                self.occurred_at,
                self.profile_type,
                self.previous_value,
                self.current_value,
                metadata_items,
            )
        )