"""Value Object para timestamps normalizados em UTC."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from ultrastats_ai.domain.shared.errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class UtcTimestamp:
    """Representa um instante absoluto normalizado para UTC."""

    value: datetime | str

    def __post_init__(self) -> None:
        """Converte a entrada para datetime consciente em UTC."""
        normalized = self._normalize(self.value)

        object.__setattr__(self, "value", normalized)

    @classmethod
    def _normalize(cls, value: datetime | str) -> datetime:
        """Normaliza datetime ou string ISO para UTC."""
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, str):
            stripped = value.strip()

            if not stripped:
                raise DomainValidationError(
                    "UtcTimestamp não pode ser vazio."
                )

            iso_value = stripped

            if iso_value.endswith(("Z", "z")):
                iso_value = iso_value[:-1] + "+00:00"

            try:
                parsed = datetime.fromisoformat(iso_value)
            except ValueError:
                raise DomainValidationError(
                    "UtcTimestamp deve possuir um timestamp ISO válido."
                ) from None
        else:
            raise TypeError(
                "UtcTimestamp deve receber datetime ou str."
            )

        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise DomainValidationError(
                "UtcTimestamp exige um datetime com timezone."
            )

        return parsed.astimezone(timezone.utc)

    @classmethod
    def now(cls) -> UtcTimestamp:
        """Cria um timestamp correspondente ao instante UTC atual."""
        return cls(datetime.now(timezone.utc))

    @property
    def isoformat(self) -> str:
        """Retorna a representação ISO usando o sufixo Z."""
        return self.value.isoformat().replace("+00:00", "Z")