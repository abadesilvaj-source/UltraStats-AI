"""API pública de integração com providers."""

from ultrastats_ai.infrastructure.providers.core import (
    FootballDataProvider,
    InMemoryRawPayloadStore,
    ProviderCapability,
    ProviderCollector,
    ProviderConfig,
    ProviderConfigurationError,
    ProviderDashboard,
    ProviderError,
    ProviderHealth,
    ProviderHTTPClient,
    ProviderRegistry,
    ProviderResponseError,
    RateLimiter,
    RawProviderPayload,
    RawPayloadStore,
    build_football_data_provider,
)
from ultrastats_ai.infrastructure.providers.persistence import (
    SqlAlchemyHealthStore,
    SqlAlchemyRawPayloadStore,
    payload_fingerprint,
)

__all__ = [
    "FootballDataProvider",
    "InMemoryRawPayloadStore",
    "ProviderCapability",
    "ProviderCollector",
    "ProviderConfig",
    "ProviderConfigurationError",
    "ProviderDashboard",
    "ProviderError",
    "ProviderHealth",
    "ProviderHTTPClient",
    "ProviderRegistry",
    "ProviderResponseError",
    "RateLimiter",
    "RawProviderPayload",
    "RawPayloadStore",
    "build_football_data_provider",
    "SqlAlchemyHealthStore",
    "SqlAlchemyRawPayloadStore",
    "payload_fingerprint",
]
