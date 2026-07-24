from datetime import datetime, timezone
from decimal import Decimal as D
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.experience import (
    AlertRule,
    ExperienceMode,
    Favorite,
    Notification,
    NotificationChannel,
    UserExperienceProfile,
)
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    UserExperienceProfileRecord,
)
from ultrastats_ai.infrastructure.experience import ExperienceStore


NOW = datetime.now(timezone.utc)


def test_profile_favorites_alerts_notifications_push_and_report() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            store = ExperienceStore(session)
            profile = UserExperienceProfile("user", ExperienceMode.SIMPLE)
            store.save_profile(profile, NOW)
            store.save_profile(UserExperienceProfile("user", ExperienceMode.ADVANCED), NOW)
            favorite = Favorite("user", "team", "team-1", "Team")
            first = store.add_favorite(favorite, NOW)
            session.flush()
            updated = store.add_favorite(Favorite("user", "team", "team-1", "A Team"), NOW)
            assert first is updated and updated.label == "A Team"
            store.add_favorite(Favorite("user", "league", "league-1", "League"), NOW)
            alert = AlertRule(
                "alert",
                "user",
                "score",
                ">=",
                D(".8"),
                NotificationChannel.PUSH,
            )
            store.save_alert(alert)
            store.save_alert(alert)
            notification = Notification(
                "notification",
                "user",
                "Title",
                "Body",
                NotificationChannel.IN_APP,
                NOW,
            )
            store.notify(notification)
            assert store.mark_read("missing") is False
            assert store.mark_read("notification") is True
            push = store.subscribe_push("user", "https://push.test/1", "key", NOW)
            session.flush()
            assert store.subscribe_push("user", "https://push.test/1", "new-key", NOW) is push
            report = store.save_report("user", "Report", "# Report", NOW)
            session.commit()
            assert session.get(UserExperienceProfileRecord, "user").mode == "advanced"
            assert [item.label for item in store.favorites("user")] == ["A Team", "League"]
            assert store.notification_feed("user")[0].read
            assert report.title == "Report"
            assert store.remove_favorite("user", "team", "team-1") == 1
            assert store.remove_favorite("user", "team", "missing") == 0
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    ("user", "endpoint", "key"),
    [
        ("", "https://push.test", "key"),
        ("user", "http://push.test", "key"),
        ("user", "https://push.test", ""),
    ],
)
def test_push_validation(user, endpoint, key) -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            with pytest.raises(ValueError, match="Push"):
                ExperienceStore(session).subscribe_push(user, endpoint, key, NOW)
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    ("user", "title", "content"),
    [("", "Title", "Body"), ("user", "", "Body"), ("user", "Title", "")],
)
def test_report_validation(user, title, content) -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            with pytest.raises(ValueError, match="Relatório"):
                ExperienceStore(session).save_report(user, title, content, NOW)
    finally:
        engine.dispose()


def test_empty_feeds() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            store = ExperienceStore(session)
            assert store.favorites("none") == ()
            assert store.notification_feed("none") == ()
    finally:
        engine.dispose()


def test_g12_migration_upgrade_and_downgrade() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "migrations"
        / "versions"
        / "e5c01372e228_create_user_experience.py"
    )
    spec = importlib.util.spec_from_file_location("g12_migration", path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    names = {
        "user_experience_profiles",
        "user_favorites",
        "user_alerts",
        "user_notifications",
        "push_subscriptions",
        "automatic_reports",
    }
    try:
        with engine.begin() as connection:
            migration.op = Operations(MigrationContext.configure(connection))
            migration.upgrade()
            assert names <= set(connection.dialect.get_table_names(connection))
            migration.downgrade()
            assert names.isdisjoint(connection.dialect.get_table_names(connection))
    finally:
        engine.dispose()
