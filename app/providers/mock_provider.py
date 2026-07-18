from __future__ import annotations

from app.providers.base import (
    BaseProvider,
    ProviderCapability,
    ProviderHealthResult,
    ProviderInfo,
)
from app.providers.registry import (
    provider_registry,
)


@provider_registry.provider
class MockProvider(
    BaseProvider
):
    """
    Provider local utilizado em testes e
    desenvolvimento.

    Ele não realiza chamadas externas.
    """

    info = ProviderInfo(
        name="mock",
        display_name="Mock Provider",
        capabilities=frozenset(
            {
                ProviderCapability.COMPETITIONS,
                ProviderCapability.TEAMS,
                ProviderCapability.MATCHES,
                ProviderCapability.STANDINGS,
            }
        ),
        requires_api_key=False,
        official_api=False,
    )

    def health_check(
        self,
    ) -> ProviderHealthResult:
        return ProviderHealthResult(
            provider_name=self.name,
            available=True,
            message=(
                "Mock Provider disponível."
            ),
            details={
                "mode": "local",
                "external_requests": False,
            },
        )