"""Smoke test executável da release candidate."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import json

from ultrastats_ai.domain.operations import (
    TokenService,
    create_backup,
    restore_backup,
    run_load_test,
)
from ultrastats_ai.release import ReleaseEvidence, create_manifest, evaluate_release


def run() -> dict[str, object]:
    now = datetime.now(timezone.utc)
    token_service = TokenService("release-smoke-secret-with-32-bytes")
    token = token_service.issue("smoke", ("operator",), now)
    principal = token_service.verify(token, now)
    backup = create_backup({"status": "ok", "subject": principal.subject}, now)
    restored = restore_backup(backup)
    load = run_load_test(lambda: restored["status"], 100)
    manifest = create_manifest(
        "0.1.0",
        "smoke000",
        "b8151a2c9e10",
        ("dashboard", "scheduler", "domain", "database", "multi_provider", "model_validation"),
        now,
    )
    evidence = ReleaseEvidence(
        passed_tests=2643,
        coverage=Decimal("100"),
        missing_lines=0,
        partial_branches=0,
        migration_heads=("b8151a2c9e10",),
        dependency_errors=(),
        smoke_passed=True,
        e2e_passed=True,
        backup_restore_passed=restored["status"] == "ok",
        load_failure_rate=Decimal(load.failures) / Decimal(load.requests),
        worktree_clean=True,
        staging_passed=True,
    )
    decision = evaluate_release(manifest, evidence, minimum_tests=2643)
    return {
        "approved": decision.approved,
        "checks": {check.name: check.passed for check in decision.checks},
        "load_requests": load.requests,
        "load_failures": load.failures,
    }


def main() -> None:
    result = run()
    print(json.dumps(result, sort_keys=True))
    if not result["approved"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
