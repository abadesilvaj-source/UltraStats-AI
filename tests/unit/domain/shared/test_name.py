"""Testes do Value Object base para nomes."""

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.name import Name


def test_name_accepts_regular_name() -> None:
    name = Name("UltraStats AI")

    assert name.value == "UltraStats AI"


def test_name_normalizes_surrounding_and_internal_spaces() -> None:
    name = Name("  UltraStats    AI  ")

    assert name.value == "UltraStats AI"


def test_name_accepts_accented_characters() -> None:
    name = Name("São Paulo")

    assert name.value == "São Paulo"


def test_name_accepts_apostrophe() -> None:
    name = Name("O'Connor")

    assert name.value == "O'Connor"


def test_name_accepts_hyphen() -> None:
    name = Name("Paris Saint-Germain")

    assert name.value == "Paris Saint-Germain"


def test_name_accepts_periods() -> None:
    name = Name("F.C. Porto")

    assert name.value == "F.C. Porto"


def test_name_accepts_numbers() -> None:
    name = Name("Schalke 04")

    assert name.value == "Schalke 04"


def test_name_accepts_non_latin_characters() -> None:
    name = Name("東京")

    assert name.value == "東京"


def test_name_rejects_single_character() -> None:
    with pytest.raises(
        DomainValidationError,
        match="pelo menos 2",
    ):
        Name("A")


@pytest.mark.parametrize(
    "invalid_value",
    [
        "--",
        "..",
        "__",
        "''",
        "@#",
    ],
)
def test_name_requires_alphanumeric_character(
    invalid_value: str,
) -> None:
    with pytest.raises(
        DomainValidationError,
        match="caractere alfanumérico",
    ):
        Name(invalid_value)


def test_name_rejects_value_above_maximum_length() -> None:
    with pytest.raises(
        DomainValidationError,
        match="no máximo 150",
    ):
        Name("A" * 151)


def test_name_string_representation_returns_value() -> None:
    name = Name("UltraStats AI")

    assert str(name) == "UltraStats AI"