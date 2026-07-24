from datetime import datetime, timezone
from decimal import Decimal

import pytest

from ultrastats_ai.release import (
    ProviderAcceptance,
    StagingEvidence,
    evaluate_staging,
)


NOW = datetime(2026, 7, 24, tzinfo=timezone.utc)


def evidence(**changes) -> StagingEvidence:
    values = {
        "version": "0.1.0-rc.2",
        "migration_head": "head",
        "expected_migration_head": "head",
        "services": {
            "postgres": True,
            "migrations": True,
            "scheduler": True,
            "dashboard": True,
        },
        "providers": (
            ProviderAcceptance("openligadb", True, True, True),
            ProviderAcceptance("api_football", False, False, False, required=False),
        ),
        "dashboard_http_status": 200,
        "load_requests": 100,
        "load_failures": 0,
        "backup_restore_passed": True,
        "security_passed": True,
        "rollback_passed": True,
        "operator_accepted": True,
        "observed_minutes": 30,
        "collected_at": NOW,
    }
    values.update(changes)
    return StagingEvidence(**values)


def test_acceptance_approves_required_and_warns_optional() -> None:
    decision = evaluate_staging(evidence(), minimum_observation_minutes=30)
    assert decision.approved
    assert decision.blockers == ()
    optional = next(check for check in decision.checks if check.name == "optional_providers")
    assert not optional.passed and not optional.blocking


def test_acceptance_reports_every_blocker() -> None:
    providers = (ProviderAcceptance("required", True, False, True),)
    decision = evaluate_staging(
        evidence(
            migration_head="old",
            services={"postgres": False},
            providers=providers,
            dashboard_http_status=503,
            load_failures=10,
            backup_restore_passed=False,
            security_passed=False,
            rollback_passed=False,
            operator_accepted=False,
            observed_minutes=1,
        ),
        maximum_failure_rate=Decimal("0.01"),
        minimum_observation_minutes=30,
    )
    assert not decision.approved
    assert len(decision.blockers) == 10


def test_acceptance_requires_at_least_one_required_provider() -> None:
    decision = evaluate_staging(
        evidence(providers=(ProviderAcceptance("optional", True, True, True, False),))
    )
    assert "required_providers" in decision.blockers


@pytest.mark.parametrize(
    "changes",
    [
        {"version": ""},
        {"expected_migration_head": ""},
        {"load_requests": 0},
        {"load_failures": -1},
        {"load_requests": 1, "load_failures": 2},
        {"observed_minutes": -1},
    ],
)
def test_staging_evidence_rejects_invalid_values(changes) -> None:
    with pytest.raises(ValueError):
        evidence(**changes)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"required_services": ()},
        {"maximum_failure_rate": Decimal("-0.1")},
        {"maximum_failure_rate": Decimal("1.1")},
        {"minimum_observation_minutes": -1},
    ],
)
def test_gate_rejects_invalid_limits(kwargs) -> None:
    with pytest.raises(ValueError):
        evaluate_staging(evidence(), **kwargs)
