"""Observações, conflitos e resultado auditável de Data Fusion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from ultrastats_ai.domain.policies import ProviderPriorityPolicy


@dataclass(frozen=True, slots=True)
class ProviderObservation:
    provider: str
    canonical_id: str
    values: Mapping[str, object]
    observed_at: datetime
    payload_fingerprint: str

    def __post_init__(self) -> None:
        if not all((self.provider.strip(), self.canonical_id.strip(), self.payload_fingerprint.strip())):
            raise ValueError("Observação exige origem, entidade e rastreabilidade.")


@dataclass(frozen=True, slots=True)
class FusionConflict:
    field: str
    values: Mapping[str, object]
    selected_provider: str


@dataclass(frozen=True, slots=True)
class FusionResult:
    canonical_id: str
    values: Mapping[str, object]
    provenance: Mapping[str, str]
    conflicts: tuple[FusionConflict, ...]
    fused_at: datetime


class DataFusionEngine:
    def __init__(self, priority: ProviderPriorityPolicy) -> None:
        self.priority = priority

    def fuse(
        self,
        observations: tuple[ProviderObservation, ...],
        fused_at: datetime,
    ) -> FusionResult:
        if not observations:
            raise ValueError("Data Fusion exige observações.")
        canonical_id = observations[0].canonical_id
        if any(item.canonical_id != canonical_id for item in observations):
            raise ValueError("Observações pertencem a entidades diferentes.")
        fields = sorted({field for item in observations for field in item.values})
        values: dict[str, object] = {}
        provenance: dict[str, str] = {}
        conflicts: list[FusionConflict] = []
        for field in fields:
            available = {
                item.provider: item.values[field]
                for item in observations
                if field in item.values and item.values[field] is not None
            }
            if not available:
                continue
            selected = self.priority.choose(tuple(available))
            values[field] = available[selected]
            provenance[field] = selected
            if len({repr(value) for value in available.values()}) > 1:
                conflicts.append(FusionConflict(field, available, selected))
        return FusionResult(
            canonical_id,
            values,
            provenance,
            tuple(conflicts),
            fused_at,
        )
