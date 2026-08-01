"""Testes de MovementType."""

import pytest

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.movement_type import MovementType
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_movement_type_inherits_from_domain_enum() -> None:
    assert issubclass(MovementType, DomainEnum)


def test_movement_type_contains_expected_values() -> None:
    assert MovementType.values() == (
        "transfer",
        "loan",
        "loan_return",
        "free_transfer",
        "release",
        "contract_renewal",
        "promotion",
        "demotion",
        "retirement",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("transfer", MovementType.TRANSFER),
        ("TRANSFER", MovementType.TRANSFER),
        ("loan", MovementType.LOAN),
        ("Loan Return", MovementType.LOAN_RETURN),
        ("free-transfer", MovementType.FREE_TRANSFER),
        (
            "CONTRACT RENEWAL",
            MovementType.CONTRACT_RENEWAL,
        ),
        ("promotion", MovementType.PROMOTION),
        ("retirement", MovementType.RETIREMENT),
    ],
)
def test_movement_type_parses_valid_values(
    value: str,
    expected: MovementType,
) -> None:
    assert MovementType.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "sale",
        "purchase",
        "unknown_movement",
    ],
)
def test_movement_type_rejects_invalid_values(value: str) -> None:
    with pytest.raises(DomainValidationError):
        MovementType.parse(value)


def test_movement_type_returns_expected_names() -> None:
    assert MovementType.names() == (
        "TRANSFER",
        "LOAN",
        "LOAN_RETURN",
        "FREE_TRANSFER",
        "RELEASE",
        "CONTRACT_RENEWAL",
        "PROMOTION",
        "DEMOTION",
        "RETIREMENT",
    )


def test_movement_type_has_value_handles_invalid_types() -> None:
    assert MovementType.has_value("loan return")
    assert not MovementType.has_value(123)
    assert not MovementType.has_value(None)