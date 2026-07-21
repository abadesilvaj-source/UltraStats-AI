"""Testes de UtcTimestamp."""

from datetime import datetime, timedelta, timezone

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.temporal.utc_timestamp import UtcTimestamp


def test_utc_timestamp_accepts_utc_datetime() -> None:
    value = datetime(2026, 7, 21, 15, 30, tzinfo=timezone.utc)

    timestamp = UtcTimestamp(value)

    assert timestamp.value == value
    assert timestamp.value.tzinfo == timezone.utc


def test_utc_timestamp_converts_other_timezone_to_utc() -> None:
    brazil_offset = timezone(timedelta(hours=-3))
    value = datetime(2026, 7, 21, 12, 30, tzinfo=brazil_offset)

    timestamp = UtcTimestamp(value)

    assert timestamp.value == datetime(
        2026,
        7,
        21,
        15,
        30,
        tzinfo=timezone.utc,
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "2026-07-21T15:30:00Z",
            datetime(2026, 7, 21, 15, 30, tzinfo=timezone.utc),
        ),
        (
            "2026-07-21T15:30:00+00:00",
            datetime(2026, 7, 21, 15, 30, tzinfo=timezone.utc),
        ),
        (
            "2026-07-21T12:30:00-03:00",
            datetime(2026, 7, 21, 15, 30, tzinfo=timezone.utc),
        ),
    ],
)
def test_utc_timestamp_accepts_iso_strings(
    value: str,
    expected: datetime,
) -> None:
    timestamp = UtcTimestamp(value)

    assert timestamp.value == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "not-a-timestamp",
        "2026-13-21T15:30:00Z",
    ],
)
def test_utc_timestamp_rejects_invalid_strings(value: str) -> None:
    with pytest.raises(DomainValidationError):
        UtcTimestamp(value)


def test_utc_timestamp_rejects_naive_datetime() -> None:
    with pytest.raises(
        DomainValidationError,
        match="exige um datetime com timezone",
    ):
        UtcTimestamp(datetime(2026, 7, 21, 15, 30))


def test_utc_timestamp_rejects_unsupported_type() -> None:
    with pytest.raises(
        TypeError,
        match="datetime ou str",
    ):
        UtcTimestamp(123)  # type: ignore[arg-type]


def test_utc_timestamp_exposes_iso_format_with_z() -> None:
    timestamp = UtcTimestamp("2026-07-21T15:30:00+00:00")

    assert timestamp.isoformat == "2026-07-21T15:30:00Z"


def test_utc_timestamp_now_is_timezone_aware_and_utc() -> None:
    timestamp = UtcTimestamp.now()

    assert timestamp.value.tzinfo == timezone.utc


def test_utc_timestamp_is_immutable() -> None:
    timestamp = UtcTimestamp("2026-07-21T15:30:00Z")

    with pytest.raises((AttributeError, TypeError)):
        timestamp.value = datetime.now(timezone.utc)  # type: ignore[misc]