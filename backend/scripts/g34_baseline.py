"""Gera o manifesto seguro e a fotografia operacional da G34."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import os
from pathlib import Path
import platform
import subprocess
from typing import Any, Mapping
from urllib.request import urlopen

from sqlalchemy import inspect, text

from app.database.session import SessionLocal


SAFE_CONFIGURATION = (
    "ACTIVE_PROVIDERS", "SYNC_INTERVAL_MINUTES", "LIVE_SYNC_INTERVAL_MINUTES",
    "ODDS_SYNC_INTERVAL_MINUTES", "ODDS_SYNC_WINDOW_DAYS", "ODDS_MAX_AGE_HOURS",
    "AUTO_STATS_LOOKBACK_DAYS", "PLAYER_IMPACT_ENABLED",
    "PLAYER_IMPACT_MIN_COVERAGE", "PLAYER_IMPACT_MAX_XG_ADJUSTMENT",
    "PAPER_TRADING_PORTFOLIO", "PAPER_TRADING_MIN_ODDS",
    "PAPER_TRADING_MAX_ODDS", "PAPER_TRADING_MIN_PROBABILITY",
    "PAPER_TRADING_MAX_HORIZON_HOURS", "PAPER_TRADING_DAILY_EXPOSURE",
    "PAPER_TRADING_MATCH_EXPOSURE", "PAPER_TRADING_EXECUTABLE_MARKETS",
    "PAPER_TRADING_BLOCKED_MARKETS", "PAPER_POLICY_MIN_SEGMENT_SAMPLES",
)

COUNT_TABLES = (
    "competitions", "teams", "matches", "markets", "predictions",
    "recommendation_opportunities", "feature_snapshots", "odds_snapshots",
    "data_quality_incidents", "model_deployments", "temporal_backtests",
    "paper_bets", "paper_portfolios", "users", "bet_slips",
)

PACKAGE_NAMES = ("fastapi", "sqlalchemy", "alembic", "psycopg", "apscheduler", "httpx")
SOURCE_DIRECTORIES = ("api", "app", "scripts", "src", "migrations")


def safe_configuration(environment: Mapping[str, str]) -> dict[str, str | None]:
    """Retorna somente chaves explicitamente públicas; nunca infere segredos."""
    return {key: environment.get(key) for key in SAFE_CONFIGURATION}


def checksum_payload(payload: Mapping[str, Any]) -> str:
    normalized = {key: value for key, value in payload.items() if key not in {"captured_at", "checksum"}}
    encoded = json.dumps(
        normalized, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, default=str,
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def verify_baseline(payload: Mapping[str, Any]) -> bool:
    checksum = payload.get("checksum")
    return isinstance(checksum, str) and checksum == checksum_payload(payload)


def source_tree_checksum(root: Path) -> str:
    """Identifica exatamente o backend executado, mesmo com Git ainda sujo."""
    files: list[Path] = []
    for directory in SOURCE_DIRECTORIES:
        location = root / directory
        if location.exists():
            files.extend(path for path in location.rglob("*.py") if "__pycache__" not in path.parts)
    for name in ("pyproject.toml", "requirements.txt", "requirements-dev.txt", "alembic.ini"):
        path = root / name
        if path.exists():
            files.append(path)
    digest = hashlib.sha256()
    for path in sorted(set(files), key=lambda item: item.as_posix()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _git_commit() -> str:
    try:
        return subprocess.run(
            ("git", "rev-parse", "HEAD"), check=True, capture_output=True,
            text=True, timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def _packages() -> dict[str, str]:
    values: dict[str, str] = {}
    for package in PACKAGE_NAMES:
        try:
            values[package] = version(package)
        except PackageNotFoundError:
            values[package] = "not-installed"
    return values


def _database_snapshot(session) -> dict[str, Any]:
    available = set(inspect(session.connection()).get_table_names())
    counts = {
        table: int(session.scalar(text(f'SELECT count(*) FROM "{table}"')) or 0)
        for table in COUNT_TABLES if table in available
    }
    migration_heads = []
    if "alembic_version" in available:
        migration_heads = list(session.scalars(text("SELECT version_num FROM alembic_version ORDER BY version_num")))
    paper = []
    if {"paper_portfolios", "paper_bets"}.issubset(available):
        paper = [dict(row._mapping) for row in session.execute(text("""
            SELECT p.name, p.active, p.initial_balance, p.current_balance,
                   count(b.id) AS decisions,
                   count(b.id) FILTER (WHERE b.stake > 0) AS executed,
                   count(b.id) FILTER (WHERE b.stake = 0) AS shadow,
                   coalesce(sum(b.stake), 0) AS total_stake
            FROM paper_portfolios p
            LEFT JOIN paper_bets b ON b.portfolio_id = p.id
            GROUP BY p.id ORDER BY p.created_at
        """))]
    recommendation = {}
    if "recommendation_opportunities" in available:
        row = session.execute(text("""
            SELECT count(*) AS total,
                   count(*) FILTER (WHERE safe) AS safe,
                   max(evaluated_at) AS latest_evaluated_at
            FROM recommendation_opportunities
        """)).one()
        recommendation = dict(row._mapping)
    return {
        "dialect": session.bind.dialect.name,
        "migration_heads": migration_heads,
        "counts": counts,
        "paper_portfolios": paper,
        "recommendations": recommendation,
    }


def _health_snapshot(url: str | None) -> dict[str, Any]:
    if not url:
        return {"status": "not-requested"}
    started = datetime.now(timezone.utc)
    try:
        with urlopen(url, timeout=10) as response:  # noqa: S310 - URL supplied by operator
            body = json.loads(response.read().decode("utf-8"))
        elapsed = (datetime.now(timezone.utc) - started).total_seconds() * 1000
        intelligence = body.get("intelligence") or {}
        learning = intelligence.get("learning") or {}
        latest_validation = learning.get("latest_validation") or {}
        validation_metrics = latest_validation.get("metrics") or {}
        platform_state = intelligence.get("platform") or {}
        return {
            "status": body.get("status"),
            "latency_ms": round(elapsed, 2),
            "counts": body.get("counts") or {},
            "last_sync": body.get("last_sync") or {},
            "intelligence": {
                "statistics": intelligence.get("statistics") or {},
                "recommendations": intelligence.get("recommendations") or {},
                "learning": {
                    "audited_predictions": learning.get("audited_predictions"),
                    "registered_models": learning.get("registered_models"),
                    "training_datasets": learning.get("training_datasets"),
                    "latest_validation": {
                        "approved": latest_validation.get("approved"),
                        "evaluated_at": latest_validation.get("evaluated_at"),
                        "brier_score": validation_metrics.get("brier_score"),
                        "calibration_error": validation_metrics.get("calibration_error"),
                        "samples": validation_metrics.get("samples"),
                        "drift_detected": validation_metrics.get("drift_detected"),
                        "champion": validation_metrics.get("champion"),
                        "challenger": validation_metrics.get("challenger"),
                    },
                },
                "platform": {
                    "feature_store": platform_state.get("feature_store") or {},
                    "quality": platform_state.get("quality") or {},
                    "models": platform_state.get("models") or {},
                    "decision_control": platform_state.get("decision_control") or {},
                    "task_queue": platform_state.get("task_queue") or {},
                },
            },
        }
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {"status": "unavailable", "error_type": type(error).__name__}


def build_baseline(*, session, environment: Mapping[str, str], commit: str,
                   health_url: str | None, captured_at: datetime) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": "g34-baseline-v1",
        "captured_at": captured_at.astimezone(timezone.utc).isoformat(),
        "source_commit": commit,
        "source_tree_checksum": source_tree_checksum(Path.cwd()),
        "runtime": {"python": platform.python_version(), "packages": _packages()},
        "configuration": safe_configuration(environment),
        "decision_scope": {
            "portfolio": environment.get("PAPER_TRADING_PORTFOLIO", "automatic-shadow-v2"),
            "executable_markets": sorted(filter(None, environment.get(
                "PAPER_TRADING_EXECUTABLE_MARKETS",
                "under_2_5_goals,under_3_5_goals,both_teams_to_score",
            ).split(","))),
            "policy": "selective_reserved_exposure_v2",
        },
        "database": _database_snapshot(session),
        "health": _health_snapshot(health_url),
    }
    payload["checksum"] = checksum_payload(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--health-url", default="http://localhost:8000/api/v1/health")
    parser.add_argument("--commit", default=None)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        payload = json.loads(args.verify.read_text(encoding="utf-8"))
        if not verify_baseline(payload):
            raise SystemExit("Baseline inválido: checksum não confere.")
        print(f"Baseline válido: {payload['checksum']}")
        return
    with SessionLocal() as session:
        baseline = build_baseline(
            session=session, environment=os.environ,
            commit=args.commit or _git_commit(), health_url=args.health_url,
            captured_at=datetime.now(timezone.utc),
        )
    rendered = json.dumps(baseline, ensure_ascii=False, indent=2, default=str) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
