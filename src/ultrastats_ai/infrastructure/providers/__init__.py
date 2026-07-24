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
    ProviderResponseError,
    RateLimiter,
    RawProviderPayload,
    RawPayloadStore,
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
    "ProviderResponseError",
    "RateLimiter",
    "RawProviderPayload",
    "RawPayloadStore",
]
