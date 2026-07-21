"""Testes de BetStatus."""

import pytest

from ultrastats_ai.domain.shared.enums.bet_status import BetStatus
from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_bet_status_inherits_from_domain_enum() -> None:
    assert issubclass(BetStatus, DomainEnum)


def test_bet_status_contains_expected_values() -> None:
    assert BetStatus.values() == (
        "open",
        "won",
        "lost",
        "void",
        "half_won",
        "half_lost",
        "cash_out",
        "cancelled",
        "pending",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("open", BetStatus.OPEN),
        ("OPEN", BetStatus.OPEN),
        ("won", BetStatus.WON),
        ("Lost", BetStatus.LOST),
        ("void", BetStatus.VOID),
        ("Half Won", BetStatus.HALF_WON),
        ("half-lost", BetStatus.HALF_LOST),
        ("CASH OUT", BetStatus.CASH_OUT),
        ("cancelled", BetStatus.CANCELLED),
        ("pending", BetStatus.PENDING),
    ],
)
def test_bet_status_parses_valid_values(
    value: str,
    expected: BetStatus,
) -> None:
    assert BetStatus.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "closed",
        "settled",
        "unknown_bet_status",
    ],
)
def test_bet_status_rejects_invalid_values(value: str) -> None:
    with pytest.raises(DomainValidationError):
        BetStatus.parse(value)


def test_bet_status_has_value_accepts_normalized_input() -> None:
    assert BetStatus.has_value("Half Won")
    assert BetStatus.has_value("cash-out")
    assert not BetStatus.has_value("unknown")


def test_bet_status_returns_expected_names() -> None:
    assert BetStatus.names() == (
        "OPEN",
        "WON",
        "LOST",
        "VOID",
        "HALF_WON",
        "HALF_LOST",
        "CASH_OUT",
        "CANCELLED",
        "PENDING",
    )


def test_bet_status_is_serializable_as_string() -> None:
    assert str(BetStatus.WON) == "won"