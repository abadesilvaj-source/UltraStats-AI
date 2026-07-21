"""Testes de SeasonStatus."""

import pytest

from ultrastats_ai.domain.shared.enums.season_status import SeasonStatus
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_season_status_contains_expected_values() -> None:
    assert SeasonStatus.values() == (
        "planned",
        "active",
        "suspended",
        "completed",
        "cancelled",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("planned", SeasonStatus.PLANNED),
        ("ACTIVE", SeasonStatus.ACTIVE),
        ("Suspended", SeasonStatus.SUSPENDED),
        (" completed ", SeasonStatus.COMPLETED),
        ("cancelled", SeasonStatus.CANCELLED),
    ],
)
def test_season_status_parses_valid_values(
    value: str,
    expected: SeasonStatus,
) -> None:
    assert SeasonStatus.parse(value) is expected


def test_season_status_rejects_invalid_value() -> None:
    with pytest.raises(DomainValidationError):
        SeasonStatus.parse("finished")