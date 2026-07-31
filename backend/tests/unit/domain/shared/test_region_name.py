"""Testes do Value Object RegionName."""

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.proper_name import ProperName
from ultrastats_ai.domain.shared.region_name import RegionName


def test_region_name_accepts_valid_value() -> None:
    name = RegionName("São Paulo")

    assert name.value == "São Paulo"


def test_region_name_is_proper_name() -> None:
    name = RegionName("São Paulo")

    assert isinstance(name, ProperName)


def test_region_name_normalizes_whitespace() -> None:
    name = RegionName("  New    South Wales  ")

    assert name.value == "New South Wales"


def test_region_name_preserves_unicode() -> None:
    name = RegionName("Andalucía")

    assert name.value == "Andalucía"


def test_region_name_rejects_invalid_value() -> None:
    with pytest.raises(
        DomainValidationError,
        match="caractere alfanumérico",
    ):
        RegionName("...")