"""Testes de MarketType."""

import pytest

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.market_type import MarketType
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_market_type_inherits_from_domain_enum() -> None:
    assert issubclass(MarketType, DomainEnum)


def test_market_type_contains_expected_values() -> None:
    assert MarketType.values() == (
        "match_winner",
        "double_chance",
        "draw_no_bet",
        "both_teams_to_score",
        "over_under_goals",
        "correct_score",
        "half_time",
        "half_time_full_time",
        "asian_handicap",
        "european_handicap",
        "corners",
        "cards",
        "shots",
        "player_props",
        "team_props",
        "other",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("match_winner", MarketType.MATCH_WINNER),
        ("MATCH WINNER", MarketType.MATCH_WINNER),
        ("double-chance", MarketType.DOUBLE_CHANCE),
        ("Draw No Bet", MarketType.DRAW_NO_BET),
        (
            "Both Teams To Score",
            MarketType.BOTH_TEAMS_TO_SCORE,
        ),
        (
            "OVER_UNDER_GOALS",
            MarketType.OVER_UNDER_GOALS,
        ),
        ("correct score", MarketType.CORRECT_SCORE),
        (
            "Half Time Full Time",
            MarketType.HALF_TIME_FULL_TIME,
        ),
        ("asian handicap", MarketType.ASIAN_HANDICAP),
        (
            "EUROPEAN-HANDICAP",
            MarketType.EUROPEAN_HANDICAP,
        ),
        ("player props", MarketType.PLAYER_PROPS),
        ("team-props", MarketType.TEAM_PROPS),
    ],
)
def test_market_type_parses_valid_values(
    value: str,
    expected: MarketType,
) -> None:
    assert MarketType.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "winner",
        "goals",
        "unknown_market",
    ],
)
def test_market_type_rejects_invalid_values(value: str) -> None:
    with pytest.raises(DomainValidationError):
        MarketType.parse(value)


def test_market_type_has_value_accepts_normalized_input() -> None:
    assert MarketType.has_value("Both Teams To Score")
    assert MarketType.has_value("asian-handicap")
    assert not MarketType.has_value("unknown")


def test_market_type_returns_expected_choices() -> None:
    assert (
        "match_winner",
        "MATCH_WINNER",
    ) in MarketType.choices()

    assert (
        "both_teams_to_score",
        "BOTH_TEAMS_TO_SCORE",
    ) in MarketType.choices()


def test_market_type_is_serializable_as_string() -> None:
    assert str(MarketType.MATCH_WINNER) == "match_winner"
    assert MarketType.MATCH_WINNER.value == "match_winner"