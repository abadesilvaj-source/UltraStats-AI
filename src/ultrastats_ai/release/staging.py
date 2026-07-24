"""Gate auditável de homologação operacional em staging."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ProviderAcceptance:
    name: str
    configured: bool
    reachable: bool
    contract_valid: bool
    required: bool = True

    @property
    def accepted(self) -> bool:
        return self.configured and self.reachable and self.contract_valid


@dataclass(frozen=True, slots=True)
class StagingEvidence:
    version: str
    migration_head: str
    expected_migration_head: str
    services: Mapping[str, bool]
    providers: tuple[ProviderAcceptance, ...]
    dashboard_http_status: int
    load_requests: int
    load_failures: int
    backup_restore_passed: bool
    security_passed: bool
    rollback_passed: bool
    operator_accepted: bool
    observed_minutes: int
    collected_at: datetime

    def __post_init__(self) -> None:
        if (
            not self.version.strip()
            or not self.expected_migration_head.strip()
            or self.load_requests <= 0
            or self.load_failures < 0
            or self.load_failures > self.load_requests
            or self.observed_minutes < 0
        ):
            raise ValueError("Evidência de staging inválida.")

    @property
    def failure_rate(self) -> Decimal:
        return Decimal(self.load_failures) / Decimal(self.load_requests)


@dataclass(frozen=True, slots=True)
class AcceptanceCheck:
    name: str
    passed: bool
    detail: str
    blocking: bool = True


@dataclass(frozen=True, slots=True)
class StagingDecision:
    checks: tuple[AcceptanceCheck, ...]

    @property
    def approved(self) -> bool:
        return all(check.passed for check in self.checks if check.blocking)

    @property
    def blockers(self) -> tuple[str, ...]:
        return tuple(check.name for check in self.checks if check.blocking and not check.passed)


def evaluate_staging(
    evidence: StagingEvidence,
    *,
    required_services: tuple[str, ...] = ("postgres", "migrations", "scheduler", "dashboard"),
    maximum_failure_rate: Decimal = Decimal("0.01"),
    minimum_observation_minutes: int = 0,
) -> StagingDecision:
    if (
        not required_services
        or not Decimal("0") <= maximum_failure_rate <= Decimal("1")
        or minimum_observation_minutes < 0
    ):
        raise ValueError("Limites de homologação inválidos.")
    service_failures = tuple(
        name for name in required_services if not evidence.services.get(name, False)
    )
    required_providers = tuple(provider for provider in evidence.providers if provider.required)
    provider_failures = tuple(
        provider.name for provider in required_providers if not provider.accepted
    )
    optional_failures = tuple(
        provider.name
        for provider in evidence.providers
        if not provider.required and not provider.accepted
    )
    checks = (
        AcceptanceCheck(
            "migration_head",
            evidence.migration_head == evidence.expected_migration_head,
            evidence.migration_head,
        ),
        AcceptanceCheck(
            "services",
            not service_failures,
            ",".join(service_failures) or "ok",
        ),
        AcceptanceCheck(
            "required_providers",
            bool(required_providers) and not provider_failures,
            ",".join(provider_failures) or "ok",
        ),
        AcceptanceCheck(
            "optional_providers",
            not optional_failures,
            ",".join(optional_failures) or "ok",
            blocking=False,
        ),
        AcceptanceCheck(
            "dashboard",
            evidence.dashboard_http_status == 200,
            str(evidence.dashboard_http_status),
        ),
        AcceptanceCheck(
            "load",
            evidence.failure_rate <= maximum_failure_rate,
            str(evidence.failure_rate),
        ),
        AcceptanceCheck("backup_restore", evidence.backup_restore_passed, str(evidence.backup_restore_passed)),
        AcceptanceCheck("security", evidence.security_passed, str(evidence.security_passed)),
        AcceptanceCheck("rollback", evidence.rollback_passed, str(evidence.rollback_passed)),
        AcceptanceCheck(
            "operator_acceptance",
            evidence.operator_accepted,
            str(evidence.operator_accepted),
        ),
        AcceptanceCheck(
            "observation_window",
            evidence.observed_minutes >= minimum_observation_minutes,
            f"{evidence.observed_minutes}/{minimum_observation_minutes}",
        ),
    )
    return StagingDecision(checks)
