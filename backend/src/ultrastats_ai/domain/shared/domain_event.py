"""Abstração base para eventos de domínio."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


def utc_now() -> datetime:
    """Retorna a data e hora atual em UTC."""

    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent:
    """Representa um fato relevante que ocorreu no domínio.

    Eventos de domínio devem ser imutáveis depois de criados.
    """

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    @property
    def event_name(self) -> str:
        """Retorna o nome lógico do evento."""

        return type(self).__name__