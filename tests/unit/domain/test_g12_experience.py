from datetime import datetime, timedelta, timezone
from decimal import Decimal as D

import pytest

from ultrastats_ai.domain.experience import (
    AlertRule,
    DataFreshness,
    ExperienceMode,
    Favorite,
    Notification,
    NotificationChannel,
    Scenario,
    SearchDocument,
    TimelineItem,
    UserExperienceProfile,
    automatic_report,
    build_timeline,
    compare_scenarios,
    natural_language_search,
)


NOW = datetime.now(timezone.utc)


def test_profile_favorite_notification_and_search_document_validation() -> None:
    profile = UserExperienceProfile("user", ExperienceMode.ADVANCED, high_contrast=True)
    assert profile.mode is ExperienceMode.ADVANCED
    with pytest.raises(ValueError, match="Perfil"):
        UserExperienceProfile("")
    with pytest.raises(ValueError, match="Perfil"):
        UserExperienceProfile("user", locale="")
    with pytest.raises(ValueError, match="Favorito"):
        Favorite("user", "team", "", "Team")
    with pytest.raises(ValueError, match="Notificação"):
        Notification("id", "user", "", "body", NotificationChannel.IN_APP, NOW)
    with pytest.raises(ValueError, match="Documento"):
        SearchDocument("team", "", "Team")


@pytest.mark.parametrize(
    ("operator", "value", "expected"),
    [
        (">", D("2"), True),
        (">=", D("1"), True),
        ("<", D("0"), True),
        ("<=", D("1"), True),
        ("==", D("1"), True),
        (">", D("0"), False),
    ],
)
def test_alert_operators(operator, value, expected) -> None:
    alert = AlertRule("id", "user", "score", operator, D("1"), NotificationChannel.IN_APP)
    assert alert.matches(value) is expected


def test_alert_validation() -> None:
    with pytest.raises(ValueError, match="identidade"):
        AlertRule("", "user", "score", ">", D("1"), NotificationChannel.IN_APP)
    with pytest.raises(ValueError, match="Operador"):
        AlertRule("id", "user", "score", "!=", D("1"), NotificationChannel.PUSH)


def test_natural_language_search_normalizes_ranks_and_filters() -> None:
    documents = (
        SearchDocument("page", "1", "Análises de xG", ("estatísticas",)),
        SearchDocument("page", "2", "Mercados", ("análises", "odds")),
        SearchDocument("page", "3", "Equipes", ("clubes",)),
    )
    results = natural_language_search("analises odds", documents)
    assert [item.document.entity_id for item in results] == ["1", "2"]
    assert results[0].relevance == 2
    assert natural_language_search("", documents) == ()
    assert natural_language_search("árbitros", documents) == ()


def test_scenarios_and_comparison() -> None:
    first = Scenario("A", D(".6"), D("2"), D("10"))
    second = Scenario("B", D(".7"), D("2"), D("10"))
    comparison = compare_scenarios((first, second))
    assert first.expected_profit == D("2")
    assert comparison.best is second
    assert compare_scenarios(()).best is None
    with pytest.raises(ValueError, match="probabilidade"):
        Scenario("", D(".5"), D("2"), D("10"))
    with pytest.raises(ValueError, match="probabilidade"):
        Scenario("A", D("1.1"), D("2"), D("10"))
    with pytest.raises(ValueError, match="odd"):
        Scenario("A", D(".5"), D("1"), D("10"))
    with pytest.raises(ValueError, match="stake"):
        Scenario("A", D(".5"), D("2"), D("-1"))


def test_timeline_and_freshness_statuses() -> None:
    older = TimelineItem("b", "data", "Older", NOW - timedelta(minutes=2))
    same_b = TimelineItem("b", "data", "Same B", NOW)
    same_a = TimelineItem("a", "data", "Same A", NOW)
    assert build_timeline((older, same_b, same_a)) == (same_a, same_b, older)
    assert DataFreshness(NOW, NOW).status == "fresh"
    assert DataFreshness(NOW, NOW + timedelta(hours=1)).status == "stale"
    assert DataFreshness(NOW, NOW - timedelta(seconds=1)).status == "clock_skew"
    with pytest.raises(ValueError, match="Janela"):
        DataFreshness(NOW, NOW, timedelta(0))


def test_automatic_report_is_stable_and_validated() -> None:
    report = automatic_report("Resumo", {"z": 2, "a": 1}, NOW)
    assert report.index("- a: 1") < report.index("- z: 2")
    assert NOW.isoformat() in report
    with pytest.raises(ValueError, match="Relatório"):
        automatic_report("", {"a": 1}, NOW)
    with pytest.raises(ValueError, match="Relatório"):
        automatic_report("Resumo", {}, NOW)
