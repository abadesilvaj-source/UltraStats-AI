import pytest

from app.providers import (
    BaseProvider,
    MockProvider,
    ProviderCapability,
    ProviderHealthResult,
    ProviderInfo,
    ProviderNotFoundError,
    ProviderRegistrationError,
    ProviderRegistry,
    provider_registry,
)


def test_global_registry_contains_mock() -> None:
    assert provider_registry.contains(
        "mock"
    )

    assert "mock" in (
        provider_registry.names()
    )


def test_registry_creates_mock_provider() -> None:
    provider = provider_registry.create(
        "mock"
    )

    assert isinstance(
        provider,
        MockProvider,
    )

    assert provider.name == "mock"
    assert (
        provider.display_name
        == "Mock Provider"
    )


def test_mock_provider_health_check() -> None:
    provider = provider_registry.create(
        "mock"
    )

    health_result = (
        provider.health_check()
    )

    assert health_result.available is True
    assert (
        health_result.provider_name
        == "mock"
    )


def test_mock_provider_capabilities() -> None:
    provider = provider_registry.create(
        "mock"
    )

    assert provider.supports(
        ProviderCapability.MATCHES
    )

    assert not provider.supports(
        ProviderCapability.ODDS
    )


def test_registry_normalizes_provider_name() -> None:
    provider = provider_registry.create(
        "  MOCK  "
    )

    assert provider.name == "mock"


def test_registry_raises_for_unknown_provider() -> None:
    with pytest.raises(
        ProviderNotFoundError
    ):
        provider_registry.create(
            "unknown_provider"
        )


def test_registry_rejects_duplicate_name() -> None:
    registry = ProviderRegistry()

    class FirstProvider(
        BaseProvider
    ):
        info = ProviderInfo(
            name="duplicate",
            display_name="First",
            capabilities=frozenset(),
            requires_api_key=False,
        )

        def health_check(
            self,
        ) -> ProviderHealthResult:
            return ProviderHealthResult(
                provider_name=self.name,
                available=True,
                message="OK",
            )

    class SecondProvider(
        BaseProvider
    ):
        info = ProviderInfo(
            name="duplicate",
            display_name="Second",
            capabilities=frozenset(),
            requires_api_key=False,
        )

        def health_check(
            self,
        ) -> ProviderHealthResult:
            return ProviderHealthResult(
                provider_name=self.name,
                available=True,
                message="OK",
            )

    registry.register(
        FirstProvider
    )

    with pytest.raises(
        ProviderRegistrationError
    ):
        registry.register(
            SecondProvider
        )


def test_registry_can_replace_provider() -> None:
    registry = ProviderRegistry()

    class FirstProvider(
        BaseProvider
    ):
        info = ProviderInfo(
            name="replaceable",
            display_name="First",
            capabilities=frozenset(),
            requires_api_key=False,
        )

        def health_check(
            self,
        ) -> ProviderHealthResult:
            return ProviderHealthResult(
                provider_name=self.name,
                available=True,
                message="First",
            )

    class SecondProvider(
        BaseProvider
    ):
        info = ProviderInfo(
            name="replaceable",
            display_name="Second",
            capabilities=frozenset(),
            requires_api_key=False,
        )

        def health_check(
            self,
        ) -> ProviderHealthResult:
            return ProviderHealthResult(
                provider_name=self.name,
                available=True,
                message="Second",
            )

    registry.register(
        FirstProvider
    )

    registry.register(
        SecondProvider,
        replace=True,
    )

    provider = registry.create(
        "replaceable"
    )

    assert isinstance(
        provider,
        SecondProvider,
    )