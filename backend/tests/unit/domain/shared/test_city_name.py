"""Testes do Value Object CityName."""

import pytest

from ultrastats_ai.domain.shared.city_name import CityName
from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.proper_name import ProperName


def test_city_name_accepts_valid_value() -> None:
    name = CityName("Araraquara")

    assert name.value == "Araraquara"


def test_city_name_is_proper_name() -> None:
    name = CityName("Araraquara")

    assert isinstance(name, ProperName)


def test_city_name_normalizes_whitespace() -> None:
    name = CityName("  Buenos    Aires  ")

    assert name.value == "Buenos Aires"


def test_city_name_preserves_unicode() -> None:
    name = CityName("Łódź")

    assert name.value == "Łódź"


def test_city_name_accepts_non_latin_characters() -> None:
    name = CityName("東京")

    assert name.value == "東京"


def test_city_name_rejects_invalid_value() -> None:
    with pytest.raises(
        DomainValidationError,
        match="caractere alfanumérico",
    ):
        CityName("@#")