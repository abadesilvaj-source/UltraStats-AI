from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal as D

import pytest

from ultrastats_ai.release import (
    ReleaseEvidence,
    create_manifest,
    evaluate_release,
    verify_manifest,
)


NOW = datetime.now(timezone.utc)


def manifest():
    return create_manifest(
        "0.1.0-rc.1",
        "abcdef123456",
        "a7e23594a440",
        ("scheduler", "dashboard", "scheduler"),
        NOW,
    )


def evidence(**changes):
    values = {
        "passed_tests": 2600,
        "coverage": D("100"),
        "missing_lines": 0,
        "partial_branches": 0,
        "migration_heads": ("a7e23594a440",),
        "dependency_errors": (),
        "smoke_passed": True,
        "e2e_passed": True,
        "backup_restore_passed": True,
        "load_failure_rate": D("0"),
        "worktree_clean": True,
        "staging_passed": True,
    }
    values.update(changes)
    return ReleaseEvidence(**values)


def test_manifest_is_normalized_reproducible_and_verified() -> None:
    value = manifest()
    assert value.components == ("dashboard", "scheduler")
    assert verify_manifest(value)
    assert not verify_manifest(replace(value, checksum="bad"))
    assert not verify_manifest(replace(value, version="invalid"))


@pytest.mark.parametrize(
    ("version", "commit", "head", "components", "message"),
    [
        ("0.1-rc.1", "abcdef1", "head", ("app",), "Versão"),
        ("a.1.0-rc.1", "abcdef1", "head", ("app",), "Versão"),
        ("0.1.0-rc.0", "abcdef1", "head", ("app",), "Versão"),
        ("0.1.0-rc.x", "abcdef1", "head", ("app",), "Versão"),
        ("0.1.0-rc.1-rc.2", "abcdef1", "head", ("app",), "Versão"),
        ("0.1.0-rc.1", "short", "head", ("app",), "commit"),
        ("0.1.0-rc.1", "abcdef1", "", ("app",), "migration"),
        ("0.1.0-rc.1", "abcdef1", "head", (), "componentes"),
        ("0.1.0-rc.1", "abcdef1", "head", ("",), "vazios"),
    ],
)
def test_manifest_validation(version, commit, head, components, message) -> None:
    with pytest.raises(ValueError, match=message):
        create_manifest(version, commit, head, components, NOW)


def test_release_gate_approves_complete_evidence() -> None:
    decision = evaluate_release(manifest(), evidence(), minimum_tests=2585)
    assert decision.approved
    assert len(decision.checks) == 13
    assert all(check.detail for check in decision.checks)


def test_release_gate_reports_every_failure() -> None:
    value = evidence(
        passed_tests=1,
        coverage=D("99"),
        missing_lines=1,
        partial_branches=1,
        migration_heads=("other", "second"),
        dependency_errors=("broken",),
        smoke_passed=False,
        e2e_passed=False,
        backup_restore_passed=False,
        load_failure_rate=D(".1"),
        worktree_clean=False,
        staging_passed=False,
    )
    decision = evaluate_release(
        replace(manifest(), checksum="tampered"),
        value,
        minimum_tests=2585,
        maximum_load_failure_rate=D(".01"),
    )
    assert not decision.approved
    assert not any(check.passed for check in decision.checks)


def test_stable_manifest_is_supported() -> None:
    assert create_manifest("0.1.0", "abcdef1", "head", ("app",), NOW).version == "0.1.0"


@pytest.mark.parametrize(
    "changes",
    [
        {"passed_tests": -1},
        {"coverage": D("-1")},
        {"coverage": D("101")},
        {"missing_lines": -1},
        {"partial_branches": -1},
        {"load_failure_rate": D("-1")},
        {"load_failure_rate": D("2")},
    ],
)
def test_release_evidence_validation(changes) -> None:
    with pytest.raises(ValueError, match="inválid|negativ|Taxa"):
        evidence(**changes)


@pytest.mark.parametrize(
    ("minimum", "rate"),
    [(0, D(".01")), (1, D("-1")), (1, D("2"))],
)
def test_release_gate_limit_validation(minimum, rate) -> None:
    with pytest.raises(ValueError, match="Limites"):
        evaluate_release(manifest(), evidence(), minimum_tests=minimum, maximum_load_failure_rate=rate)
