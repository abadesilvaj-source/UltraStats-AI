"""Manifesto reproduzível e gate técnico de release candidate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import hashlib
import json


@dataclass(frozen=True, slots=True)
class ReleaseManifest:
    version: str
    commit: str
    migration_head: str
    components: tuple[str, ...]
    created_at: datetime
    checksum: str


@dataclass(frozen=True, slots=True)
class ReleaseEvidence:
    passed_tests: int
    coverage: Decimal
    missing_lines: int
    partial_branches: int
    migration_heads: tuple[str, ...]
    dependency_errors: tuple[str, ...]
    smoke_passed: bool
    e2e_passed: bool
    backup_restore_passed: bool
    load_failure_rate: Decimal
    worktree_clean: bool

    def __post_init__(self) -> None:
        if self.passed_tests < 0 or not Decimal("0") <= self.coverage <= Decimal("100"):
            raise ValueError("Evidência possui testes ou cobertura inválidos.")
        if self.missing_lines < 0 or self.partial_branches < 0:
            raise ValueError("Evidência não aceita contagens negativas.")
        if not Decimal("0") <= self.load_failure_rate <= Decimal("1"):
            raise ValueError("Taxa de falha de carga inválida.")


@dataclass(frozen=True, slots=True)
class ReleaseCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True, slots=True)
class ReleaseDecision:
    checks: tuple[ReleaseCheck, ...]

    @property
    def approved(self) -> bool:
        return all(check.passed for check in self.checks)


def create_manifest(
    version: str,
    commit: str,
    migration_head: str,
    components: tuple[str, ...],
    created_at: datetime,
) -> ReleaseManifest:
    if not _valid_rc_version(version):
        raise ValueError("Versão deve seguir o formato semântico de release candidate.")
    if len(commit) < 7 or not migration_head.strip() or not components:
        raise ValueError("Manifesto exige commit, migration e componentes.")
    normalized = tuple(sorted(set(component.strip() for component in components)))
    if any(not component for component in normalized):
        raise ValueError("Componentes do manifesto não podem ser vazios.")
    payload = {
        "version": version,
        "commit": commit,
        "migration_head": migration_head,
        "components": normalized,
        "created_at": created_at.isoformat(),
    }
    checksum = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return ReleaseManifest(
        version,
        commit,
        migration_head,
        normalized,
        created_at,
        checksum,
    )


def verify_manifest(manifest: ReleaseManifest) -> bool:
    try:
        recreated = create_manifest(
            manifest.version,
            manifest.commit,
            manifest.migration_head,
            manifest.components,
            manifest.created_at,
        )
    except ValueError:
        return False
    return recreated.checksum == manifest.checksum


def evaluate_release(
    manifest: ReleaseManifest,
    evidence: ReleaseEvidence,
    *,
    minimum_tests: int,
    maximum_load_failure_rate: Decimal = Decimal(".01"),
) -> ReleaseDecision:
    if minimum_tests <= 0 or not Decimal("0") <= maximum_load_failure_rate <= Decimal("1"):
        raise ValueError("Limites do release gate são inválidos.")
    checks = (
        ReleaseCheck("manifest", verify_manifest(manifest), manifest.checksum),
        ReleaseCheck(
            "tests",
            evidence.passed_tests >= minimum_tests,
            f"{evidence.passed_tests}/{minimum_tests}",
        ),
        ReleaseCheck("coverage", evidence.coverage == Decimal("100"), str(evidence.coverage)),
        ReleaseCheck("missing_lines", evidence.missing_lines == 0, str(evidence.missing_lines)),
        ReleaseCheck(
            "partial_branches",
            evidence.partial_branches == 0,
            str(evidence.partial_branches),
        ),
        ReleaseCheck(
            "migration_head",
            evidence.migration_heads == (manifest.migration_head,),
            ",".join(evidence.migration_heads),
        ),
        ReleaseCheck(
            "dependencies",
            not evidence.dependency_errors,
            ",".join(evidence.dependency_errors) or "ok",
        ),
        ReleaseCheck("smoke", evidence.smoke_passed, str(evidence.smoke_passed)),
        ReleaseCheck("e2e", evidence.e2e_passed, str(evidence.e2e_passed)),
        ReleaseCheck(
            "backup_restore",
            evidence.backup_restore_passed,
            str(evidence.backup_restore_passed),
        ),
        ReleaseCheck(
            "load",
            evidence.load_failure_rate <= maximum_load_failure_rate,
            str(evidence.load_failure_rate),
        ),
        ReleaseCheck("worktree", evidence.worktree_clean, str(evidence.worktree_clean)),
    )
    return ReleaseDecision(checks)


def _valid_rc_version(version: str) -> bool:
    parts = version.split("-rc.")
    if len(parts) != 2 or not parts[1].isdigit() or int(parts[1]) <= 0:
        return False
    core = parts[0].split(".")
    return len(core) == 3 and all(part.isdigit() for part in core)
