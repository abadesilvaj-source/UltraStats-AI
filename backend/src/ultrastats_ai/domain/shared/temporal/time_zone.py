"""Value Object para timezones IANA."""

from __future__ import annotations

from dataclasses import dataclass
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ultrastats_ai.domain.shared.errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class TimeZone:
    """Representa um timezone válido da base IANA."""

    value: str

    def __post_init__(self) -> None:
        """Normaliza e valida o nome do timezone."""
        normalized = self._normalize(self.value)

        object.__setattr__(self, "value", normalized)

    @staticmethod
    def _normalize(value: str) -> str:
        """Remove espaços externos e valida o timezone."""
        if not isinstance(value, str):
            raise TypeError(
                "TimeZone deve ser criado a partir de uma string."
            )

        normalized = value.strip()

        if not normalized:
            raise DomainValidationError(
                "TimeZone não pode ser vazio."
            )

        try:
            zone = ZoneInfo(normalized)
        except ZoneInfoNotFoundError:
            raise DomainValidationError(
                f"TimeZone inválido ou não encontrado: {normalized}."
            ) from None

        return zone.key

    @property
    def zone_info(self) -> ZoneInfo:
        """Retorna o objeto ZoneInfo correspondente."""
        return ZoneInfo(self.value)