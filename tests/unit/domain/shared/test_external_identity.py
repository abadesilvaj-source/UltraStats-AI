"""Testes da identidade externa composta ExternalIdentity."""

import pytest

from ultrastats_ai.domain.shared import (
    ExternalIdentifier,
    ExternalIdentity,
    ProviderNamespace,
)
from ultrastats_ai.domain.shared.external_ids import (
    ExternalIdentity as ExternalIdsPackageExternalIdentity,
)


def test_external_identity_stores_provider_and_identifier() -> None:
    provider = ProviderNamespace("sportradar")
    identifier = ExternalIdentifier("sr:team:1234")

    identity = ExternalIdentity(
        provider=provider,
        identifier=identifier,
    )

    assert identity.provider is provider
    assert identity.identifier is identifier


def test_external_identity_exposes_composite_key() -> None:
    identity = ExternalIdentity(
        provider=ProviderNamespace("sportradar"),
        identifier=ExternalIdentifier("sr:team:1234"),
    )

    assert identity.key == (
        "sportradar",
        "sr:team:1234",
    )


def test_external_identity_normalizes_composed_values_before_equality() -> None:
    first = ExternalIdentity(
        provider=ProviderNamespace(" Sportradar "),
        identifier=ExternalIdentifier(" sr:team:1234 "),
    )
    second = ExternalIdentity(
        provider=ProviderNamespace("sportradar"),
        identifier=ExternalIdentifier("sr:team:1234"),
    )

    assert first == second
    assert hash(first) == hash(second)


def test_external_identity_distinguishes_different_providers() -> None:
    opta = ExternalIdentity(
        provider=ProviderNamespace("opta"),
        identifier=ExternalIdentifier("100"),
    )
    sportradar = ExternalIdentity(
        provider=ProviderNamespace("sportradar"),
        identifier=ExternalIdentifier("100"),
    )

    assert opta != sportradar
    assert opta.key != sportradar.key


def test_external_identity_distinguishes_different_identifiers() -> None:
    first = ExternalIdentity(
        provider=ProviderNamespace("opta"),
        identifier=ExternalIdentifier("100"),
    )
    second = ExternalIdentity(
        provider=ProviderNamespace("opta"),
        identifier=ExternalIdentifier("200"),
    )

    assert first != second
    assert first.key != second.key


def test_external_identity_preserves_identifier_case() -> None:
    lowercase = ExternalIdentity(
        provider=ProviderNamespace("provider"),
        identifier=ExternalIdentifier("abc123"),
    )
    uppercase = ExternalIdentity(
        provider=ProviderNamespace("provider"),
        identifier=ExternalIdentifier("ABC123"),
    )

    assert lowercase != uppercase


def test_external_identity_rejects_raw_provider_string() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "ExternalIdentity.provider deve ser um "
            "ProviderNamespace"
        ),
    ):
        ExternalIdentity(
            provider="sportradar",  # type: ignore[arg-type]
            identifier=ExternalIdentifier("sr:team:1234"),
        )


def test_external_identity_rejects_raw_identifier_string() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "ExternalIdentity.identifier deve ser um "
            "ExternalIdentifier"
        ),
    ):
        ExternalIdentity(
            provider=ProviderNamespace("sportradar"),
            identifier="sr:team:1234",  # type: ignore[arg-type]
        )


def test_external_identity_is_immutable() -> None:
    identity = ExternalIdentity(
        provider=ProviderNamespace("sportradar"),
        identifier=ExternalIdentifier("sr:team:1234"),
    )

    with pytest.raises((AttributeError, TypeError)):
        identity.provider = ProviderNamespace("opta")  # type: ignore[misc]


def test_external_identity_can_be_used_as_dictionary_key() -> None:
    identity = ExternalIdentity(
        provider=ProviderNamespace("sportradar"),
        identifier=ExternalIdentifier("sr:team:1234"),
    )

    values = {
        identity: "São Paulo FC",
    }

    equivalent_identity = ExternalIdentity(
        provider=ProviderNamespace("SPORTRADAR"),
        identifier=ExternalIdentifier("sr:team:1234"),
    )

    assert values[equivalent_identity] == "São Paulo FC"


def test_external_identity_public_apis_export_same_class() -> None:
    assert ExternalIdentity is ExternalIdsPackageExternalIdentity