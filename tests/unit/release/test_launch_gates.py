from decimal import Decimal

import pytest

from ultrastats_ai.release import (
    PilotEvidence,
    ProductionEvidence,
    PublicLaunchEvidence,
    evaluate_pilot,
    evaluate_production,
    evaluate_public_launch,
)


def production(**changes) -> ProductionEvidence:
    values = {
        "domain": "app.example.com",
        "tls_enabled": True,
        "services": {name: True for name in ("postgres", "migrations", "scheduler", "dashboard")},
        "migration_current": True,
        "secrets_externalized": True,
        "backup_restore_passed": True,
        "monitoring_enabled": True,
    }
    values.update(changes)
    return ProductionEvidence(**values)


def pilot(**changes) -> PilotEvidence:
    values = {
        "invited_users": 10,
        "active_users": 8,
        "observed_days": 14,
        "predictions": 200,
        "incidents": 0,
        "availability": Decimal("0.999"),
        "feedback_score": Decimal("4.2"),
    }
    values.update(changes)
    return PilotEvidence(**values)


def test_production_gate_approves_complete_evidence() -> None:
    decision = evaluate_production(production())
    assert decision.approved
    assert decision.blockers == ()


def test_production_gate_reports_all_failures() -> None:
    decision = evaluate_production(
        production(
            domain="localhost",
            tls_enabled=False,
            services={},
            migration_current=False,
            secrets_externalized=False,
            backup_restore_passed=False,
            monitoring_enabled=False,
        )
    )
    assert not decision.approved
    assert len(decision.blockers) == 7


def test_production_rejects_invalid_configuration() -> None:
    with pytest.raises(ValueError):
        production(domain=" ")
    with pytest.raises(ValueError):
        evaluate_production(production(), required_services=())


def test_pilot_gate_approves_complete_evidence() -> None:
    assert evaluate_pilot(pilot()).approved


def test_pilot_gate_reports_all_failures() -> None:
    decision = evaluate_pilot(
        pilot(
            active_users=1,
            observed_days=1,
            predictions=1,
            incidents=3,
            availability=Decimal("0.8"),
            feedback_score=Decimal("2"),
        )
    )
    assert len(decision.blockers) == 6


@pytest.mark.parametrize(
    "changes",
    [
        {"invited_users": 0},
        {"active_users": 11},
        {"observed_days": -1},
        {"predictions": -1},
        {"incidents": -1},
        {"availability": Decimal("1.1")},
        {"feedback_score": Decimal("5.1")},
    ],
)
def test_pilot_rejects_invalid_evidence(changes) -> None:
    with pytest.raises(ValueError):
        pilot(**changes)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"minimum_days": 0},
        {"minimum_active_users": 0},
        {"minimum_predictions": 0},
        {"minimum_availability": Decimal("-0.1")},
        {"minimum_feedback": Decimal("5.1")},
        {"maximum_incidents": -1},
    ],
)
def test_pilot_rejects_invalid_limits(kwargs) -> None:
    with pytest.raises(ValueError):
        evaluate_pilot(pilot(), **kwargs)


def test_public_launch_requires_every_control() -> None:
    evidence = PublicLaunchEvidence(True, True, True, True, True, True, True, True)
    assert evaluate_public_launch(evidence).approved
    blocked = evaluate_public_launch(
        PublicLaunchEvidence(False, False, False, False, False, False, False, False)
    )
    assert len(blocked.blockers) == 8
