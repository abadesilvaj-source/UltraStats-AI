from datetime import datetime, timedelta, timezone
from decimal import Decimal as D

import pytest

from ultrastats_ai.domain.statistics import MatchSample, StatisticalEngine


NOW = datetime.now(timezone.utc)


def sample(
    match_id,
    days,
    *,
    home=True,
    goals=D("1"),
    conceded=D("0"),
    xg=D("1.2"),
    xga=D(".8"),
    strength=D(".5"),
    points=D("3"),
    coach="coach",
    referee="referee",
    team="team",
):
    return MatchSample(
        match_id,
        team,
        "league",
        NOW - timedelta(days=days),
        home,
        goals,
        conceded,
        xg,
        xga,
        strength,
        points,
        coach,
        referee,
        D(".1"),
    )


def test_sample_and_engine_validation() -> None:
    with pytest.raises(ValueError, match="identidades"):
        sample("", 1)
    with pytest.raises(ValueError, match="negativas"):
        sample("x", 1, goals=D("-1"))
    with pytest.raises(ValueError, match="Pontos"):
        sample("x", 1, points=D("2"))
    with pytest.raises(ValueError, match="Configuração"):
        StatisticalEngine(decay=D("0"))
    with pytest.raises(ValueError, match="Configuração"):
        StatisticalEngine(target_sample=0)


def test_complete_weighted_snapshot_and_no_future_leakage() -> None:
    samples = (
        sample("old", 10, home=True, goals=D("1"), points=D("1")),
        sample("new", 2, home=False, goals=D("3"), points=D("3")),
        sample("other", 1, team="other"),
        MatchSample(
            "future",
            "team",
            "league",
            NOW + timedelta(days=1),
            True,
            D("9"),
            D("0"),
            D("9"),
            D("0"),
            D("1"),
            D("3"),
        ),
    )
    result = StatisticalEngine(decay=D(".5"), target_sample=2).calculate(
        "team", samples, NOW
    )
    assert result.sample_size == 2
    assert result.metrics["goals_for"] == (D("3") + D(".5")) / D("1.5")
    assert result.metrics["home_performance"] == D("1") / 3
    assert result.metrics["away_performance"] == 1
    assert result.distributions["goals_for"].minimum == 1
    assert result.distributions["goals_for"].maximum == 3
    assert result.trends["goals_for"] == 2
    assert result.contexts["coach_form"] > 0
    assert result.reliability <= 1


def test_single_sample_empty_split_context_and_missing_history() -> None:
    item = sample("one", 1, home=True, coach=None, referee=None)
    result = StatisticalEngine().calculate("team", (item,), NOW)
    assert result.metrics["away_performance"] == 0
    assert result.trends == {"goals_for": 0, "expected_goals_for": 0, "form": 0}
    assert result.contexts["coach_form"] == 0
    assert result.contexts["referee_points"] == 0
    with pytest.raises(ValueError, match="amostras"):
        StatisticalEngine().calculate("missing", (item,), NOW)


def test_poisson_distribution() -> None:
    probability = StatisticalEngine.poisson_probability(D("2"), 2)
    assert D("0") < probability < D("1")
    assert StatisticalEngine.poisson_probability(D("0"), 0) == 1
    with pytest.raises(ValueError, match="Poisson"):
        StatisticalEngine.poisson_probability(D("-1"), 0)
    with pytest.raises(ValueError, match="Poisson"):
        StatisticalEngine.poisson_probability(D("1"), -1)
