"""Identidade composta utilizada por sistemas externos."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.external_ids.external_identifier import (
    ExternalIdentifier,
)
from ultrastats_ai.domain.shared.external_ids.provider_namespace import (
    ProviderNamespace,
)


@dataclass(frozen=True, slots=True)
class ExternalIdentity:
    """Representa uma identidade externa composta por provider e chave."""

    provider: ProviderNamespace
    identifier: ExternalIdentifier

    def __post_init__(self) -> None:
        """Valida os tipos que compõem a identidade externa."""
        if not isinstance(self.provider, ProviderNamespace):
            raise TypeError(
                "ExternalIdentity.provider deve ser um ProviderNamespace."
            )

        if not isinstance(self.identifier, ExternalIdentifier):
            raise TypeError(
                "ExternalIdentity.identifier deve ser um ExternalIdentifier."
            )

    @property
    def key(self) -> tuple[str, str]:
        """Retorna a chave composta em formato textual."""
        return (
            self.provider.value,
            self.identifier.value,
        )