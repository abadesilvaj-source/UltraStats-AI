"""Testes do Value Object CountryName."""

import pytest

from ultrastats_ai.domain.shared.country_name import CountryName
from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.proper_name import ProperName


def test_country_name_accepts_valid_value() -> None:
    name = CountryName("Brazil")

    assert name.value == "Brazil"


def test_country_name_is_proper_name() -> None:
    name = CountryName("Brazil")

    assert isinstance(name, ProperName)


def test_country_name_normalizes_whitespace() -> None:
    name = CountryName("  United    Kingdom  ")

    assert name.value == "United Kingdom"


def test_country_name_preserves_unicode() -> None:
    name = CountryName("Côte d'Ivoire")

    assert name.value == "Côte d'Ivoire"


def test_country_name_rejects_invalid_value() -> None:
    with pytest.raises(
        DomainValidationError,
        match="caractere alfanumérico",
    ):
        CountryName("--")