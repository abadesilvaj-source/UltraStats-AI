"""Testes de TimeZone."""

from zoneinfo import ZoneInfo

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.temporal.time_zone import TimeZone


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("UTC", "UTC"),
        (" America/Sao_Paulo ", "America/Sao_Paulo"),
        ("Europe/London", "Europe/London"),
    ],
)
def test_time_zone_accepts_valid_iana_values(
    value: str,
    expected: str,
) -> None:
    time_zone = TimeZone(value)

    assert time_zone.value == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "Brazil/SaoPaulo",
        "Invalid/Zone",
        "America/Not_A_City",
    ],
)
def test_time_zone_rejects_invalid_values(value: str) -> None:
    with pytest.raises(DomainValidationError):
        TimeZone(value)


def test_time_zone_rejects_non_string() -> None:
    with pytest.raises(TypeError, match="a partir de uma string"):
        TimeZone(123)  # type: ignore[arg-type]


def test_time_zone_exposes_zone_info() -> None:
    time_zone = TimeZone("America/Sao_Paulo")

    assert isinstance(time_zone.zone_info, ZoneInfo)
    assert time_zone.zone_info.key == "America/Sao_Paulo"


def test_time_zone_is_immutable() -> None:
    time_zone = TimeZone("UTC")

    with pytest.raises((AttributeError, TypeError)):
        time_zone.value = "Europe/London"  # type: ignore[misc]