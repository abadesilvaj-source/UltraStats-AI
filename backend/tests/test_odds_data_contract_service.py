from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.services.odds_data_contract_service import OddsDataContractService
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase, DataQualityIncidentRecord, DataQuarantineRecord,
)


def _session():
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    return Session(engine)


def test_valid_odds_contract_is_accepted():
    session = _session()
    assert OddsDataContractService(session).accept(
        provider="api_football", match_id=1, bookmaker="bet365",
        market="under_2_5_goals", selection="Under 2.5",
        value=Decimal("1.90"), captured_at=datetime.now(timezone.utc),
    ) is True


def test_invalid_odds_is_quarantined_idempotently_with_reason():
    session = _session(); service = OddsDataContractService(session)
    values = dict(provider="api_football", match_id=1, bookmaker="",
                  market="result", selection="home", value=Decimal("1.9"),
                  captured_at=datetime.now(timezone.utc))
    assert service.accept(**values) is False
    assert service.accept(**values) is False
    session.commit()
    quarantine = session.scalars(select(DataQuarantineRecord)).all()
    assert len(quarantine) == 1
    assert quarantine[0].reason == "missing_bookmaker"
    assert session.scalar(select(DataQualityIncidentRecord)).details["contract"] == "g36-odds-v1"


def test_future_timestamp_and_impossible_price_are_rejected():
    now = datetime.now(timezone.utc)
    common = dict(provider="api", match_id=1, bookmaker="book", market="m", selection="s")
    assert OddsDataContractService.validate(**common, value=Decimal("1"), captured_at=now) == "decimal_odds_out_of_range"
    assert OddsDataContractService.validate(**common, value=Decimal("2"), captured_at=now + timedelta(hours=1)) == "captured_at_in_future"
