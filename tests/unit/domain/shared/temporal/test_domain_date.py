"""Testes de DomainDate."""

from datetime import date, datetime

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.temporal.domain_date import DomainDate


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-07-21", date(2026, 7, 21)),
        (" 2026-07-21 ", date(2026, 7, 21)),
        (date(2026, 7, 21), date(2026, 7, 21)),
    ],
)
def test_domain_date_accepts_valid_values(
    value: date | str,
    expected: date,
) -> None:
    domain_date = DomainDate(value)

    assert domain_date.value == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "21/07/2026",
        "2026-13-01",
        "2026-02-30",
        "not-a-date",
    ],
)
def test_domain_date_rejects_invalid_strings(value: str) -> None:
    with pytest.raises(DomainValidationError):
        DomainDate(value)


def test_domain_date_rejects_datetime() -> None:
    with pytest.raises(
        TypeError,
        match="DomainDate não aceita datetime",
    ):
        DomainDate(datetime(2026, 7, 21, 12, 0))


def test_domain_date_rejects_unsupported_type() -> None:
    with pytest.raises(
        TypeError,
        match="DomainDate deve receber date ou str",
    ):
        DomainDate(20260721)  # type: ignore[arg-type]


def test_domain_date_exposes_iso_format() -> None:
    domain_date = DomainDate("2026-07-21")

    assert domain_date.isoformat == "2026-07-21"


def test_domain_date_adds_days_without_modifying_original() -> None:
    original = DomainDate("2026-07-21")

    result = original.add_days(10)

    assert result == DomainDate("2026-07-31")
    assert original == DomainDate("2026-07-21")


def test_domain_date_rejects_non_integer_days() -> None:
    domain_date = DomainDate("2026-07-21")

    with pytest.raises(TypeError, match="número inteiro"):
        domain_date.add_days(1.5)  # type: ignore[arg-type]


def test_domain_date_calculates_days_until_another_date() -> None:
    start = DomainDate("2026-07-21")
    end = DomainDate("2026-07-31")

    assert start.days_until(end) == 10
    assert end.days_until(start) == -10


def test_domain_date_rejects_invalid_days_until_argument() -> None:
    with pytest.raises(TypeError, match="outro DomainDate"):
        DomainDate("2026-07-21").days_until(  # type: ignore[arg-type]
            "2026-07-31"
        )


def test_domain_date_is_immutable() -> None:
    domain_date = DomainDate("2026-07-21")

    with pytest.raises((AttributeError, TypeError)):
        domain_date.value = date(2026, 7, 22)  # type: ignore[misc]
