"""Identificadores externos compartilhados do domínio."""

from ultrastats_ai.domain.shared.external_ids.external_identifier import (
    ExternalIdentifier,
)
from ultrastats_ai.domain.shared.external_ids.external_identity import (
    ExternalIdentity,
)
from ultrastats_ai.domain.shared.external_ids.provider_namespace import (
    ProviderNamespace,
)

__all__ = [
    "ExternalIdentifier",
    "ExternalIdentity",
    "ProviderNamespace",
]