"""Persistência e orquestração reprocessável da G7."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.data_fusion import FusionResult
from ultrastats_ai.domain.identity import (
    IdentityCandidate,
    IdentityDecision,
    IdentityNormalizer,
    IdentityResolutionEngine,
    NormalizedIdentity,
    QuarantinedData,
    ResolutionStatus,
)
from ultrastats_ai.infrastructure.database.models import (
    DataQuarantineRecord,
    FusionResultRecord,
    IdentityDecisionRecord,
)
from ultrastats_ai.infrastructure.providers import RawProviderPayload, payload_fingerprint


class IdentityFusionStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_decision(self, decision: IdentityDecision) -> None:
        record = self.session.scalar(
            select(IdentityDecisionRecord).where(
                IdentityDecisionRecord.provider == decision.provider,
                IdentityDecisionRecord.external_id == decision.external_id,
            )
        )
        if record is None:
            record = IdentityDecisionRecord(
                provider=decision.provider,
                external_id=decision.external_id,
                decided_at=decision.decided_at,
                status=decision.status.value,
                reason=decision.reason,
            )
            self.session.add(record)
        record.status = decision.status.value
        record.candidate_id = decision.candidate.canonical_id if decision.candidate else None
        record.score = str(decision.candidate.score) if decision.candidate else None
        record.evidence = (
            {key: str(value) for key, value in decision.candidate.evidence.items()}
            if decision.candidate
            else None
        )
        record.reason = decision.reason
        record.reviewer = decision.reviewer
        record.decided_at = decision.decided_at

    def review_queue(self) -> tuple[IdentityDecision, ...]:
        records = self.session.scalars(
            select(IdentityDecisionRecord)
            .where(IdentityDecisionRecord.status == ResolutionStatus.REVIEW.value)
            .order_by(IdentityDecisionRecord.decided_at)
        ).all()
        return tuple(self._decision(record) for record in records)

    def save_fusion(self, result: FusionResult) -> None:
        self.session.add(
            FusionResultRecord(
                canonical_id=result.canonical_id,
                values=dict(result.values),
                provenance=dict(result.provenance),
                conflicts=[
                    {
                        "field": conflict.field,
                        "values": dict(conflict.values),
                        "selected_provider": conflict.selected_provider,
                    }
                    for conflict in result.conflicts
                ],
                fused_at=result.fused_at,
            )
        )

    def quarantine(self, item: QuarantinedData) -> None:
        record = self.session.scalar(
            select(DataQuarantineRecord).where(
                DataQuarantineRecord.payload_fingerprint == item.payload_fingerprint
            )
        )
        if record is None:
            self.session.add(
                DataQuarantineRecord(
                    provider=item.provider,
                    resource=item.resource,
                    payload_fingerprint=item.payload_fingerprint,
                    reason=item.reason,
                    quarantined_at=item.quarantined_at,
                    attempts=item.attempts,
                )
            )
        else:
            record.reason = item.reason
            record.attempts = item.attempts

    def pending_quarantine(self) -> tuple[QuarantinedData, ...]:
        records = self.session.scalars(
            select(DataQuarantineRecord)
            .where(DataQuarantineRecord.resolved_at.is_(None))
            .order_by(DataQuarantineRecord.quarantined_at)
        ).all()
        return tuple(
            QuarantinedData(
                record.provider,
                record.resource,
                record.payload_fingerprint,
                record.reason,
                record.quarantined_at,
                record.attempts,
            )
            for record in records
        )

    def resolve_quarantine(self, fingerprint: str, resolved_at: datetime) -> None:
        record = self.session.scalar(
            select(DataQuarantineRecord).where(
                DataQuarantineRecord.payload_fingerprint == fingerprint
            )
        )
        if record is None:
            raise LookupError("Item de quarentena não encontrado.")
        record.resolved_at = resolved_at

    @staticmethod
    def _decision(record: IdentityDecisionRecord) -> IdentityDecision:
        candidate = (
            IdentityCandidate(
                record.candidate_id,
                Decimal(record.score),
                record.evidence or {},
            )
            if record.candidate_id and record.score
            else None
        )
        return IdentityDecision(
            record.provider,
            record.external_id,
            ResolutionStatus(record.status),
            record.decided_at,
            candidate,
            record.reason,
            record.reviewer,
        )


class IdentityPipeline:
    def __init__(
        self,
        store: IdentityFusionStore,
        canonical: Mapping[str, tuple[NormalizedIdentity, ...]],
        *,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self.store, self.canonical, self.clock = store, canonical, clock
        self.normalizer = IdentityNormalizer()
        self.resolver = IdentityResolutionEngine()

    def process(self, raw: RawProviderPayload) -> IdentityDecision:
        try:
            external_id = str(raw.payload["id"])
            name = str(raw.payload["name"])
            country_value = raw.payload.get("country")
            normalized = self.normalizer.normalize(
                name,
                str(country_value) if country_value else None,
            )
        except (KeyError, ValueError) as error:
            fingerprint = payload_fingerprint(raw)
            self.store.quarantine(
                QuarantinedData(
                    raw.provider,
                    raw.resource,
                    fingerprint,
                    str(error),
                    self.clock(),
                )
            )
            raise ValueError("Payload enviado para quarentena.") from error
        candidates = self.resolver.candidates(normalized, self.canonical)
        decision = self.resolver.decide(raw.provider, external_id, candidates, self.clock())
        self.store.save_decision(decision)
        return decision

    def reprocess(
        self,
        raw: RawProviderPayload,
        quarantine_fingerprint: str,
    ) -> IdentityDecision:
        decision = self.process(raw)
        self.store.resolve_quarantine(quarantine_fingerprint, self.clock())
        return decision
