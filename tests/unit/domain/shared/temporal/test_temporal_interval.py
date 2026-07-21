"""Testes de TemporalInterval."""

from datetime import timedelta

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.temporal.temporal_interval import (
    TemporalInterval,
)
from ultrastats_ai.domain.shared.temporal.utc_timestamp import UtcTimestamp


def create_interval() -> TemporalInterval:
    return TemporalInterval(
        start=UtcTimestamp("2026-07-21T10:00:00Z"),
        end=UtcTimestamp("2026-07-21T11:00:00Z"),
    )


def test_temporal_interval_stores_start_and_end() -> None:
    interval = create_interval()

    assert interval.start == UtcTimestamp("2026-07-21T10:00:00Z")
    assert interval.end == UtcTimestamp("2026-07-21T11:00:00Z")


def test_temporal_interval_rejects_raw_start_value() -> None:
    with pytest.raises(
        TypeError,
        match="start deve ser um UtcTimestamp",
    ):
        TemporalInterval(
            start="2026-07-21T10:00:00Z",  # type: ignore[arg-type]
            end=UtcTimestamp("2026-07-21T11:00:00Z"),
        )


def test_temporal_interval_rejects_raw_end_value() -> None:
    with pytest.raises(
        TypeError,
        match="end deve ser um UtcTimestamp",
    ):
        TemporalInterval(
            start=UtcTimestamp("2026-07-21T10:00:00Z"),
            end="2026-07-21T11:00:00Z",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (
            "2026-07-21T10:00:00Z",
            "2026-07-21T10:00:00Z",
        ),
        (
            "2026-07-21T11:00:00Z",
            "2026-07-21T10:00:00Z",
        ),
    ],
)
def test_temporal_interval_rejects_invalid_order(
    start: str,
    end: str,
) -> None:
    with pytest.raises(
        DomainValidationError,
        match="start anterior a end",
    ):
        TemporalInterval(
            start=UtcTimestamp(start),
            end=UtcTimestamp(end),
        )


def test_temporal_interval_calculates_duration() -> None:
    interval = create_interval()

    assert interval.duration == timedelta(hours=1)
    assert interval.duration_seconds == 3600.0


def test_temporal_interval_contains_start() -> None:
    interval = create_interval()

    assert interval.contains(
        UtcTimestamp("2026-07-21T10:00:00Z")
    )


def test_temporal_interval_contains_internal_timestamp() -> None:
    interval = create_interval()

    assert interval.contains(
        UtcTimestamp("2026-07-21T10:30:00Z")
    )


def test_temporal_interval_does_not_contain_end() -> None:
    interval = create_interval()

    assert not interval.contains(
        UtcTimestamp("2026-07-21T11:00:00Z")
    )


def test_temporal_interval_rejects_invalid_contains_argument() -> None:
    interval = create_interval()

    with pytest.raises(TypeError, match="exige um UtcTimestamp"):
        interval.contains("2026-07-21T10:30:00Z")  # type: ignore[arg-type]


def test_temporal_intervals_overlap() -> None:
    first = create_interval()
    second = TemporalInterval(
        start=UtcTimestamp("2026-07-21T10:30:00Z"),
        end=UtcTimestamp("2026-07-21T11:30:00Z"),
    )

    assert first.overlaps(second)
    assert second.overlaps(first)


def test_adjacent_temporal_intervals_do_not_overlap() -> None:
    first = create_interval()
    second = TemporalInterval(
        start=UtcTimestamp("2026-07-21T11:00:00Z"),
        end=UtcTimestamp("2026-07-21T12:00:00Z"),
    )

    assert not first.overlaps(second)


def test_temporal_interval_is_immutable() -> None:
    interval = create_interval()

    with pytest.raises((AttributeError, TypeError)):
        interval.start = UtcTimestamp(  # type: ignore[misc]
            "2026-07-21T09:00:00Z"
        )