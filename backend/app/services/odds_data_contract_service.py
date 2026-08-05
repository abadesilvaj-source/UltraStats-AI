from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from ultrastats_ai.infrastructure.database.models import (
    DataQualityIncidentRecord, DataQuarantineRecord,
)


class OddsDataContractService:
    """Valida uma odd antes de associá-la à partida canônica."""

    VERSION = "g36-odds-v1"

    def __init__(self, session: Session) -> None:
        self.session = session

    def accept(self, *, provider: str, match_id: int, bookmaker: str,
               market: str, selection: str, value: Decimal,
               captured_at: datetime) -> bool:
        reason = self.validate(
            provider=provider, match_id=match_id, bookmaker=bookmaker,
            market=market, selection=selection, value=value,
            captured_at=captured_at,
        )
        if reason is None:
            return True
        identity = "|".join(map(str, (
            provider, match_id, bookmaker, market, selection, value, captured_at
        )))
        fingerprint = sha256(identity.encode()).hexdigest()
        now = datetime.now(timezone.utc)
        quarantine = self.session.scalar(select(DataQuarantineRecord).where(
            DataQuarantineRecord.payload_fingerprint == fingerprint
        ))
        if quarantine is None:
            self.session.add(DataQuarantineRecord(
                provider=provider or "unknown", resource="odds",
                payload_fingerprint=fingerprint, reason=reason,
                quarantined_at=now, attempts=0,
            ))
        incident = self.session.scalar(select(DataQualityIncidentRecord).where(
            DataQualityIncidentRecord.fingerprint == fingerprint
        ))
        if incident is None:
            self.session.add(DataQualityIncidentRecord(
                fingerprint=fingerprint, kind="invalid_odds_contract",
                severity="warning", entity_type="match", entity_id=str(match_id),
                details={"reason": reason, "contract": self.VERSION},
                detected_at=now,
            ))
        return False

    @staticmethod
    def validate(*, provider: str, match_id: int, bookmaker: str, market: str,
                 selection: str, value: Decimal,
                 captured_at: datetime) -> str | None:
        for field, content in (("provider", provider), ("bookmaker", bookmaker),
                               ("market", market), ("selection", selection)):
            if not str(content).strip():
                return f"missing_{field}"
        if int(match_id) <= 0:
            return "invalid_match_id"
        try:
            decimal = Decimal(str(value))
        except (InvalidOperation, ValueError):
            return "invalid_decimal_odds"
        if not decimal.is_finite() or not Decimal("1.001") <= decimal <= Decimal("1000"):
            return "decimal_odds_out_of_range"
        aware = captured_at.replace(tzinfo=timezone.utc) if captured_at.tzinfo is None else captured_at.astimezone(timezone.utc)
        if aware > datetime.now(timezone.utc) + timedelta(minutes=5):
            return "captured_at_in_future"
        return None
