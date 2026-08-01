"""Histórico imutável do contexto competitivo."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from ultrastats_ai.domain.competition.errors import (
    DuplicateHistoryFieldError,
    EmptyHistoryChangesError,
)
from ultrastats_ai.domain.shared import (
    CanonicalId,
    UtcTimestamp,
)


class CompetitionEntityKind(str, Enum):
    COMPETITION = "competition"
    SEASON = "season"
    STAGE = "stage"
    ROUND = "round"
    TIE = "tie"


class CompetitionChangeType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


@dataclass(frozen=True, slots=True)
class CompetitionFieldChange:
    field_name: str
    previous_value: str | None
    current_value: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.field_name, str):
            raise TypeError("field_name deve ser string.")

        normalized_name = self.field_name.strip()

        if not normalized_name:
            raise ValueError(
                "field_name não pode ser vazio."
            )

        if (
            self.previous_value is not None
            and not isinstance(self.previous_value, str)
        ):
            raise TypeError(
                "previous_value deve ser string ou None."
            )

        if (
            self.current_value is not None
            and not isinstance(self.current_value, str)
        ):
            raise TypeError(
                "current_value deve ser string ou None."
            )

        previous = (
            self.previous_value.strip()
            if self.previous_value is not None
            else None
        )

        current = (
            self.current_value.strip()
            if self.current_value is not None
            else None
        )

        if previous == current:
            raise ValueError(
                "previous_value e current_value "
                "devem ser diferentes."
            )

        object.__setattr__(
            self,
            "field_name",
            normalized_name,
        )
        object.__setattr__(
            self,
            "previous_value",
            previous,
        )
        object.__setattr__(
            self,
            "current_value",
            current,
        )


@dataclass(frozen=True, slots=True)
class CompetitionHistoryEntry:
    id: CanonicalId
    entity_id: CanonicalId
    entity_kind: CompetitionEntityKind
    change_type: CompetitionChangeType
    occurred_at: UtcTimestamp
    changes: tuple[CompetitionFieldChange, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        if not isinstance(self.id, CanonicalId):
            raise TypeError("id deve ser CanonicalId.")

        if not isinstance(self.entity_id, CanonicalId):
            raise TypeError(
                "entity_id deve ser CanonicalId."
            )

        if not isinstance(
            self.entity_kind,
            CompetitionEntityKind,
        ):
            raise TypeError(
                "entity_kind deve ser "
                "CompetitionEntityKind."
            )

        if not isinstance(
            self.change_type,
            CompetitionChangeType,
        ):
            raise TypeError(
                "change_type deve ser "
                "CompetitionChangeType."
            )

        if not isinstance(
            self.occurred_at,
            UtcTimestamp,
        ):
            raise TypeError(
                "occurred_at deve ser UtcTimestamp."
            )

        if not isinstance(self.changes, tuple):
            raise TypeError("changes deve ser tuple.")

        field_names: set[str] = set()

        for change in self.changes:
            if not isinstance(
                change,
                CompetitionFieldChange,
            ):
                raise TypeError(
                    "changes deve conter "
                    "CompetitionFieldChange."
                )

            normalized = change.field_name.casefold()

            if normalized in field_names:
                raise DuplicateHistoryFieldError(
                    "Um campo não pode aparecer duas vezes."
                )

            field_names.add(normalized)

        if (
            self.change_type
            is CompetitionChangeType.UPDATED
            and not self.changes
        ):
            raise EmptyHistoryChangesError(
                "Uma atualização deve possuir alterações."
            )

    @classmethod
    def from_iterable(
        cls,
        *,
        id: CanonicalId,
        entity_id: CanonicalId,
        entity_kind: CompetitionEntityKind,
        change_type: CompetitionChangeType,
        occurred_at: UtcTimestamp,
        changes: Iterable[CompetitionFieldChange],
    ) -> CompetitionHistoryEntry:
        if isinstance(changes, (str, bytes)):
            raise TypeError(
                "changes deve ser um iterável de "
                "CompetitionFieldChange."
            )

        return cls(
            id=id,
            entity_id=entity_id,
            entity_kind=entity_kind,
            change_type=change_type,
            occurred_at=occurred_at,
            changes=tuple(changes),
        )

    @property
    def changed_fields(self) -> tuple[str, ...]:
        return tuple(
            change.field_name
            for change in self.changes
        )