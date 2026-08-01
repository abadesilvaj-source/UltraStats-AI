"""Gates auditáveis para produção, piloto e lançamento público."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping


@dataclass(frozen=True, slots=True)
class GateCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True, slots=True)
class GateDecision:
    checks: tuple[GateCheck, ...]

    @property
    def approved(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def blockers(self) -> tuple[str, ...]:
        return tuple(check.name for check in self.checks if not check.passed)


@dataclass(frozen=True, slots=True)
class ProductionEvidence:
    domain: str
    tls_enabled: bool
    services: Mapping[str, bool]
    migration_current: bool
    secrets_externalized: bool
    backup_restore_passed: bool
    monitoring_enabled: bool

    def __post_init__(self) -> None:
        if not self.domain.strip():
            raise ValueError("Domínio de produção é obrigatório.")


@dataclass(frozen=True, slots=True)
class PilotEvidence:
    invited_users: int
    active_users: int
    observed_days: int
    predictions: int
    incidents: int
    availability: Decimal
    feedback_score: Decimal

    def __post_init__(self) -> None:
        if (
            self.invited_users <= 0
            or not 0 <= self.active_users <= self.invited_users
            or self.observed_days < 0
            or self.predictions < 0
            or self.incidents < 0
            or not Decimal("0") <= self.availability <= Decimal("1")
            or not Decimal("0") <= self.feedback_score <= Decimal("5")
        ):
            raise ValueError("Evidência de piloto inválida.")


@dataclass(frozen=True, slots=True)
class PublicLaunchEvidence:
    legal_review_accepted: bool
    privacy_contact_configured: bool
    consent_versioned: bool
    age_gate_enabled: bool
    responsible_gaming_enabled: bool
    self_exclusion_enabled: bool
    pilot_approved: bool
    production_approved: bool


def evaluate_production(
    evidence: ProductionEvidence,
    *,
    required_services: tuple[str, ...] = ("postgres", "migrations", "scheduler", "backend", "frontend"),
) -> GateDecision:
    if not required_services:
        raise ValueError("Serviços obrigatórios não podem ser vazios.")
    unavailable = tuple(
        service for service in required_services if not evidence.services.get(service, False)
    )
    return GateDecision(
        (
            GateCheck("domain", "." in evidence.domain, evidence.domain),
            GateCheck("tls", evidence.tls_enabled, str(evidence.tls_enabled)),
            GateCheck("services", not unavailable, ",".join(unavailable) or "ok"),
            GateCheck("migration", evidence.migration_current, str(evidence.migration_current)),
            GateCheck("secrets", evidence.secrets_externalized, str(evidence.secrets_externalized)),
            GateCheck(
                "backup_restore",
                evidence.backup_restore_passed,
                str(evidence.backup_restore_passed),
            ),
            GateCheck("monitoring", evidence.monitoring_enabled, str(evidence.monitoring_enabled)),
        )
    )


def evaluate_pilot(
    evidence: PilotEvidence,
    *,
    minimum_days: int = 7,
    minimum_active_users: int = 5,
    minimum_predictions: int = 100,
    minimum_availability: Decimal = Decimal("0.99"),
    minimum_feedback: Decimal = Decimal("3.5"),
    maximum_incidents: int = 2,
) -> GateDecision:
    if (
        minimum_days <= 0
        or minimum_active_users <= 0
        or minimum_predictions <= 0
        or not Decimal("0") <= minimum_availability <= Decimal("1")
        or not Decimal("0") <= minimum_feedback <= Decimal("5")
        or maximum_incidents < 0
    ):
        raise ValueError("Limites de piloto inválidos.")
    return GateDecision(
        (
            GateCheck("observation_window", evidence.observed_days >= minimum_days, str(evidence.observed_days)),
            GateCheck("active_users", evidence.active_users >= minimum_active_users, str(evidence.active_users)),
            GateCheck("predictions", evidence.predictions >= minimum_predictions, str(evidence.predictions)),
            GateCheck("availability", evidence.availability >= minimum_availability, str(evidence.availability)),
            GateCheck("feedback", evidence.feedback_score >= minimum_feedback, str(evidence.feedback_score)),
            GateCheck("incidents", evidence.incidents <= maximum_incidents, str(evidence.incidents)),
        )
    )


def evaluate_public_launch(evidence: PublicLaunchEvidence) -> GateDecision:
    values = (
        ("legal_review", evidence.legal_review_accepted),
        ("privacy_contact", evidence.privacy_contact_configured),
        ("versioned_consent", evidence.consent_versioned),
        ("age_gate", evidence.age_gate_enabled),
        ("responsible_gaming", evidence.responsible_gaming_enabled),
        ("self_exclusion", evidence.self_exclusion_enabled),
        ("pilot", evidence.pilot_approved),
        ("production", evidence.production_approved),
    )
    return GateDecision(tuple(GateCheck(name, passed, str(passed)) for name, passed in values))
