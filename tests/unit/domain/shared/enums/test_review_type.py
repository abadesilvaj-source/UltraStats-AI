"""Testes de ReviewType."""

import pytest

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.review_type import ReviewType
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_review_type_inherits_from_domain_enum() -> None:
    assert issubclass(ReviewType, DomainEnum)


def test_review_type_contains_expected_values() -> None:
    assert ReviewType.values() == (
        "goal",
        "penalty",
        "red_card",
        "mistaken_identity",
        "offside",
        "handball",
        "foul",
        "ball_out_of_play",
        "disciplinary_action",
        "administrative",
        "other",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("goal", ReviewType.GOAL),
        ("PENALTY", ReviewType.PENALTY),
        ("red card", ReviewType.RED_CARD),
        (
            "Mistaken Identity",
            ReviewType.MISTAKEN_IDENTITY,
        ),
        ("offside", ReviewType.OFFSIDE),
        ("handball", ReviewType.HANDBALL),
        (
            "ball-out-of-play",
            ReviewType.BALL_OUT_OF_PLAY,
        ),
        (
            "DISCIPLINARY ACTION",
            ReviewType.DISCIPLINARY_ACTION,
        ),
        ("administrative", ReviewType.ADMINISTRATIVE),
    ],
)
def test_review_type_parses_valid_values(
    value: str,
    expected: ReviewType,
) -> None:
    assert ReviewType.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "var",
        "check",
        "unknown_review",
    ],
)
def test_review_type_rejects_invalid_values(value: str) -> None:
    with pytest.raises(DomainValidationError):
        ReviewType.parse(value)


def test_review_type_returns_expected_names() -> None:
    assert "MISTAKEN_IDENTITY" in ReviewType.names()
    assert "BALL_OUT_OF_PLAY" in ReviewType.names()


def test_review_type_is_serializable_as_string() -> None:
    assert str(ReviewType.OFFSIDE) == "offside"