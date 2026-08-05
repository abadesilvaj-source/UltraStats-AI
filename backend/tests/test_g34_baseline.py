from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from scripts.g34_baseline import (
    build_baseline, checksum_payload, safe_configuration, source_tree_checksum,
    verify_baseline,
)


def test_safe_configuration_never_exports_unapproved_secrets():
    result = safe_configuration({
        "ACTIVE_PROVIDERS": "api_football",
        "API_FOOTBALL_KEY": "must-not-leak",
        "DATABASE_URL": "must-not-leak",
        "AUTH_SECRET": "must-not-leak",
    })

    assert result["ACTIVE_PROVIDERS"] == "api_football"
    assert "API_FOOTBALL_KEY" not in result
    assert "DATABASE_URL" not in result
    assert "AUTH_SECRET" not in result


def test_baseline_is_reproducible_for_the_same_state(monkeypatch):
    monkeypatch.setattr("scripts.g34_baseline._packages", lambda: {"test": "1"})
    session = Session(create_engine("sqlite://"))
    captured = datetime(2026, 8, 2, tzinfo=timezone.utc)

    first = build_baseline(
        session=session, environment={}, commit="abcdef123", health_url=None,
        captured_at=captured,
    )
    second = build_baseline(
        session=session, environment={}, commit="abcdef123", health_url=None,
        captured_at=captured.replace(hour=1),
    )

    assert first["checksum"] == second["checksum"]
    assert first["checksum"] == checksum_payload(first)
    assert verify_baseline(first)
    assert not verify_baseline({**first, "source_commit": "changed"})
    assert first["decision_scope"]["executable_markets"] == [
        "both_teams_to_score", "under_2_5_goals", "under_3_5_goals",
    ]


def test_source_tree_checksum_tracks_content_not_timestamps(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    source = scripts / "job.py"
    source.write_text("value = 1\n", encoding="utf-8")
    first = source_tree_checksum(tmp_path)
    source.touch()
    assert source_tree_checksum(tmp_path) == first
    source.write_text("value = 2\n", encoding="utf-8")
    assert source_tree_checksum(tmp_path) != first
