"""API pública do contexto de experiência."""

from ultrastats_ai.domain.experience.engine import (
    AlertRule,
    DataFreshness,
    ExperienceMode,
    Favorite,
    Notification,
    NotificationChannel,
    Scenario,
    ScenarioComparison,
    SearchDocument,
    SearchResult,
    TimelineItem,
    UserExperienceProfile,
    automatic_report,
    build_timeline,
    compare_scenarios,
    natural_language_search,
)

__all__ = [
    "AlertRule",
    "DataFreshness",
    "ExperienceMode",
    "Favorite",
    "Notification",
    "NotificationChannel",
    "Scenario",
    "ScenarioComparison",
    "SearchDocument",
    "SearchResult",
    "TimelineItem",
    "UserExperienceProfile",
    "automatic_report",
    "build_timeline",
    "compare_scenarios",
    "natural_language_search",
]
