"""Testes da API pública dos tipos temporais."""

from ultrastats_ai.domain.shared import (
    DomainDate,
    TemporalInterval,
    TimeZone,
    UtcTimestamp,
)
from ultrastats_ai.domain.shared.temporal import (
    DomainDate as TemporalDomainDate,
    TemporalInterval as TemporalPackageInterval,
    TimeZone as TemporalTimeZone,
    UtcTimestamp as TemporalUtcTimestamp,
)


def test_temporal_types_are_exported_by_public_apis() -> None:
    assert DomainDate is TemporalDomainDate
    assert TemporalInterval is TemporalPackageInterval
    assert TimeZone is TemporalTimeZone
    assert UtcTimestamp is TemporalUtcTimestamp