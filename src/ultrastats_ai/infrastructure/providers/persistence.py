"""Stores SQLAlchemy duráveis para coleta e observabilidade de providers."""

from __future__ import annotations

from hashlib import sha256
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from ultrastats_ai.infrastructure.database.models import (
    ProviderHealthRecord,
    RawProviderPayloadRecord,
)
from ultrastats_ai.infrastructure.providers.core import (
    ProviderHealth,
    RawProviderPayload,
)


def payload_fingerprint(payload: RawProviderPayload) -> str:
    canonical = json.dumps(payload.payload, sort_keys=True, separators=(",", ":"), default=str)
    identity = f"{payload.provider}|{payload.resource}|{payload.external_id}|{canonical}"
    return sha256(identity.encode()).hexdigest()


class SqlAlchemyRawPayloadStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, payload: RawProviderPayload) -> bool:
        fingerprint = payload_fingerprint(payload)
        exists = self.session.scalar(
            select(RawProviderPayloadRecord.id).where(
                RawProviderPayloadRecord.fingerprint == fingerprint
            )
        )
        if exists is not None:
            return False
        self.session.add(
            RawProviderPayloadRecord(
                provider=payload.provider,
                resource=payload.resource,
                external_id=payload.external_id,
                fingerprint=fingerprint,
                payload=dict(payload.payload),
                collected_at=payload.collected_at,
            )
        )
        return True


class SqlAlchemyHealthStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, health: ProviderHealth) -> None:
        self.session.add(
            ProviderHealthRecord(
                provider=health.provider,
                available=health.available,
                latency_ms=health.latency_ms,
                message=health.message,
                checked_at=health.checked_at,
            )
        )

    def latest(self) -> tuple[ProviderHealth, ...]:
        records = self.session.scalars(
            select(ProviderHealthRecord).order_by(ProviderHealthRecord.checked_at.desc())
        ).all()
        seen: set[str] = set()
        result: list[ProviderHealth] = []
        for record in records:
            if record.provider in seen:
                continue
            seen.add(record.provider)
            result.append(
                ProviderHealth(
                    record.provider,
                    record.available,
                    record.latency_ms,
                    record.message,
                    record.checked_at,
                )
            )
        return tuple(result)
