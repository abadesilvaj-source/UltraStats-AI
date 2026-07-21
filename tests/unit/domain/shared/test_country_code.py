"""Testes do tipo canônico CountryCode."""

import pytest

from ultrastats_ai.domain.shared import CountryCode
from ultrastats_ai.domain.shared.codes import (
    CountryCode as CodesPackageCountryCode,
)
from ultrastats_ai.domain.shared.codes.code_value import CodeValue


def test_country_code_inherits_from_code_value() -> None:
    code = CountryCode("BRA")

    assert isinstance(code, CodeValue)


def test_country_code_accepts_valid_alpha3_code() -> None:
    code = CountryCode("BRA")

    assert code.value == "BRA"


def test_country_code_normalizes_value() -> None:
    code = CountryCode(" bra ")

    assert code.value == "BRA"


@pytest.mark.parametrize(
    "value",
    [
        "BR",
        "BRAA",
        "B",
        "ABCDE",
    ],
)
def test_country_code_rejects_values_with_invalid_length(value: str) -> None:
    with pytest.raises(
        ValueError,
        match="CountryCode deve possuir exatamente 3 caracteres",
    ):
        CountryCode(value)


@pytest.mark.parametrize(
    "value",
    [
        "B1A",
        "BR_",
        "B-A",
        "B.A",
    ],
)
def test_country_code_rejects_non_letter_characters(value: str) -> None:
    with pytest.raises(
        ValueError,
        match="CountryCode aceita apenas letras de A a Z",
    ):
        CountryCode(value)


def test_country_code_equality_uses_normalized_value() -> None:
    first = CountryCode("bra")
    second = CountryCode("BRA")

    assert first == second
    assert hash(first) == hash(second)


def test_country_code_is_immutable() -> None:
    code = CountryCode("BRA")

    with pytest.raises((AttributeError, TypeError)):
        code.value = "ARG"  # type: ignore[misc]


def test_country_code_public_apis_export_same_class() -> None:
    assert CountryCode is CodesPackageCountryCode