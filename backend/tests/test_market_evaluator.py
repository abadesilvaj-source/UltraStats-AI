import pytest

from app.utils.market_evaluator import evaluate_market


def test_over_2_5_goals_won() -> None:
    result = evaluate_market(
        market_code="over_2_5_goals",
        selection="Mais de 2.5 gols",
        home_score=2,
        away_score=1,
    )

    assert result == "won"


def test_over_2_5_goals_lost() -> None:
    result = evaluate_market(
        market_code="over_2_5_goals",
        selection="Mais de 2.5 gols",
        home_score=1,
        away_score=0,
    )

    assert result == "lost"


def test_under_2_5_goals_won() -> None:
    result = evaluate_market(
        market_code="under_2_5_goals",
        selection="Menos de 2.5 gols",
        home_score=1,
        away_score=1,
    )

    assert result == "won"


def test_both_teams_to_score_yes_won() -> None:
    result = evaluate_market(
        market_code="both_teams_to_score",
        selection="Sim",
        home_score=2,
        away_score=1,
    )

    assert result == "won"


def test_both_teams_to_score_yes_lost() -> None:
    result = evaluate_market(
        market_code="both_teams_to_score",
        selection="Sim",
        home_score=2,
        away_score=0,
    )

    assert result == "lost"


def test_over_8_5_corners_won() -> None:
    result = evaluate_market(
        market_code="over_8_5_corners",
        selection="Mais de 8.5 escanteios",
        home_score=1,
        away_score=1,
        corners_home=5,
        corners_away=4,
    )

    assert result == "won"


def test_over_8_5_corners_missing_data() -> None:
    with pytest.raises(ValueError):
        evaluate_market(
            market_code="over_8_5_corners",
            selection="Mais de 8.5 escanteios",
            home_score=1,
            away_score=1,
        )


def test_match_winner_home() -> None:
    result = evaluate_market(
        market_code="match_winner",
        selection="Mandante",
        home_score=2,
        away_score=1,
    )

    assert result == "won"


def test_negative_score_is_invalid() -> None:
    with pytest.raises(ValueError):
        evaluate_market(
            market_code="over_2_5_goals",
            selection="Mais de 2.5 gols",
            home_score=-1,
            away_score=2,
        )