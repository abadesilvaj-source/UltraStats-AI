"""Testes do tipo canônico ExternalIdentifier."""

import pytest

from ultrastats_ai.domain.shared import ExternalIdentifier
from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.external_ids import (
    ExternalIdentifier as ExternalIdsPackageExternalIdentifier,
)
from ultrastats_ai.domain.shared.text_value import TextValue


def test_external_identifier_inherits_from_text_value() -> None:
    identifier = ExternalIdentifier("sr:team:1234")

    assert isinstance(identifier, TextValue)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("sr:team:1234", "sr:team:1234"),
        ("  sr:team:1234  ", "sr:team:1234"),
        ("t12345", "t12345"),
        ("10293", "10293"),
        ("pK7Q0mTn", "pK7Q0mTn"),
        ("team_1234", "team_1234"),
        ("team-1234", "team-1234"),
        ("provider.entity.1234", "provider.entity.1234"),
        ("entity/1234", "entity/1234"),
    ],
)
def test_external_identifier_accepts_valid_values(
    value: str,
    expected: str,
) -> None:
    identifier = ExternalIdentifier(value)

    assert identifier.value == expected


@pytest.mark.parametrize(
    "value",
    [
        "sr team 1234",
        "team\t1234",
        "team\n1234",
        "team\r1234",
    ],
)
def test_external_identifier_rejects_internal_whitespace(
    value: str,
) -> None:
    with pytest.raises(
        DomainValidationError,
        match="ExternalIdentifier não pode possuir espaços internos",
    ):
        ExternalIdentifier(value)


def test_external_identifier_rejects_control_characters() -> None:
    value = "team" + chr(7) + "1234"

    with pytest.raises(
        DomainValidationError,
        match="ExternalIdentifier não pode possuir caracteres de controle",
    ):
        ExternalIdentifier(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "   ",
        "\t",
        "\n",
    ],
)
def test_external_identifier_rejects_empty_values(value: str) -> None:
    with pytest.raises(
        DomainValidationError,
        match="ExternalIdentifier não pode ser vazio",
    ):
        ExternalIdentifier(value)


def test_external_identifier_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="ExternalIdentifier deve ser criado a partir de uma string",
    ):
        ExternalIdentifier(123)  # type: ignore[arg-type]


def test_external_identifier_rejects_value_longer_than_maximum() -> None:
    value = "a" * 129

    with pytest.raises(
        DomainValidationError,
        match=r"ExternalIdentifier deve possuir no máximo 128 caractere\(s\)",
    ):
        ExternalIdentifier(value)


def test_external_identifier_accepts_value_at_maximum_length() -> None:
    value = "a" * 128

    identifier = ExternalIdentifier(value)

    assert identifier.value == value
    assert len(identifier.value) == 128


def test_external_identifier_preserves_case() -> None:
    lowercase = ExternalIdentifier("abc123")
    uppercase = ExternalIdentifier("ABC123")

    assert lowercase.value == "abc123"
    assert uppercase.value == "ABC123"
    assert lowercase != uppercase


def test_external_identifier_equality_uses_normalized_value() -> None:
    first = ExternalIdentifier("  sr:team:1234  ")
    second = ExternalIdentifier("sr:team:1234")

    assert first == second
    assert hash(first) == hash(second)


def test_external_identifier_is_immutable() -> None:
    identifier = ExternalIdentifier("sr:team:1234")

    with pytest.raises((AttributeError, TypeError)):
        identifier.value = "sr:team:9999"  # type: ignore[misc]


def test_external_identifier_public_apis_export_same_class() -> None:
    assert ExternalIdentifier is ExternalIdsPackageExternalIdentifier