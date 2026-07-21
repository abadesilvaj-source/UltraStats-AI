"""Testes do tipo canônico ProviderNamespace."""

import pytest

from ultrastats_ai.domain.shared import ProviderNamespace
from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.external_ids import (
    ProviderNamespace as ExternalIdsPackageProviderNamespace,
)
from ultrastats_ai.domain.shared.text_value import TextValue


def test_provider_namespace_inherits_from_text_value() -> None:
    namespace = ProviderNamespace("opta")

    assert isinstance(namespace, TextValue)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("opta", "opta"),
        ("SPORTRADAR", "sportradar"),
        (" Football Data ", "football_data"),
        ("API   Football", "api_football"),
        ("provider-v2", "provider-v2"),
        ("provider.v2", "provider.v2"),
    ],
)
def test_provider_namespace_normalizes_valid_values(
    value: str,
    expected: str,
) -> None:
    namespace = ProviderNamespace(value)

    assert namespace.value == expected


@pytest.mark.parametrize(
    "value",
    [
        "_opta",
        "opta_",
        "opta__api",
        "opta..api",
        "opta--api",
        "@opta",
        "opta/api",
        "opta#api",
    ],
)
def test_provider_namespace_rejects_invalid_format(value: str) -> None:
    with pytest.raises(
        DomainValidationError,
        match="ProviderNamespace aceita apenas letras minúsculas",
    ):
        ProviderNamespace(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "   ",
    ],
)
def test_provider_namespace_rejects_empty_values(value: str) -> None:
    with pytest.raises(
        DomainValidationError,
        match="ProviderNamespace não pode ser vazio",
    ):
        ProviderNamespace(value)


def test_provider_namespace_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="ProviderNamespace deve ser criado a partir de uma string",
    ):
        ProviderNamespace(123)  # type: ignore[arg-type]


def test_provider_namespace_rejects_value_longer_than_maximum() -> None:
    value = "a" * 65

    with pytest.raises(
        DomainValidationError,
        match=r"ProviderNamespace deve possuir no máximo 64 caractere\(s\)",
    ):
        ProviderNamespace(value)


def test_provider_namespace_accepts_value_at_maximum_length() -> None:
    value = "a" * 64

    namespace = ProviderNamespace(value)

    assert namespace.value == value
    assert len(namespace.value) == 64


def test_provider_namespace_equality_uses_normalized_value() -> None:
    first = ProviderNamespace("Football Data")
    second = ProviderNamespace("football_data")

    assert first == second
    assert hash(first) == hash(second)


def test_provider_namespace_is_immutable() -> None:
    namespace = ProviderNamespace("opta")

    with pytest.raises((AttributeError, TypeError)):
        namespace.value = "sportradar"  # type: ignore[misc]


def test_provider_namespace_public_apis_export_same_class() -> None:
    assert ProviderNamespace is ExternalIdsPackageProviderNamespace