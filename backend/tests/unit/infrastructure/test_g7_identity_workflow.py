from datetime import datetime, timezone
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.data_fusion import (
    DataFusionEngine,
    ProviderObservation,
)
from ultrastats_ai.domain.identity import (
    IdentityDecision,
    NormalizedIdentity,
    QuarantinedData,
    ResolutionStatus,
)
from ultrastats_ai.domain.policies import ProviderPriorityPolicy
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    DataQuarantineRecord,
    FusionResultRecord,
    IdentityDecisionRecord,
)
from ultrastats_ai.infrastructure.identity import IdentityFusionStore, IdentityPipeline
from ultrastats_ai.infrastructure.providers import RawProviderPayload, payload_fingerprint


NOW = datetime.now(timezone.utc)


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as value:
        yield value
    engine.dispose()


def raw(payload, external_id="raw-1"):
    return RawProviderPayload("provider", "teams", external_id, payload, NOW)


def test_pipeline_decision_upsert_review_queue_and_manual_review(session) -> None:
    store = IdentityFusionStore(session)
    pipeline = IdentityPipeline(
        store,
        {"team-1": (NormalizedIdentity("sao paulo"),)},
        clock=lambda: NOW,
    )
    decision = pipeline.process(raw({"id": 42, "name": "Sao Paulo"}))
    assert decision.status is ResolutionStatus.MATCHED
    store.save_decision(decision)
    session.commit()
    assert session.scalars(select(IdentityDecisionRecord)).all().__len__() == 1

    pending = IdentityDecision(
        "provider", "43", ResolutionStatus.REVIEW, NOW, decision.candidate, "review"
    )
    store.save_decision(pending)
    session.commit()
    queue = store.review_queue()
    assert len(queue) == 1
    assert queue[0].external_id == pending.external_id
    assert queue[0].candidate.canonical_id == pending.candidate.canonical_id
    approved = queue[0].review(True, "operator", "confirmed")
    store.save_decision(approved)
    session.commit()
    assert store.review_queue() == ()


def test_quarantine_idempotency_resolution_and_reprocessing(session) -> None:
    store = IdentityFusionStore(session)
    pipeline = IdentityPipeline(
        store,
        {"team-1": (NormalizedIdentity("benfica"),)},
        clock=lambda: NOW,
    )
    invalid = raw({"id": 1})
    fingerprint = payload_fingerprint(invalid)
    with pytest.raises(ValueError, match="quarentena"):
        pipeline.process(invalid)
    pending = store.pending_quarantine()
    assert pending[0].payload_fingerprint == fingerprint
    store.quarantine(pending[0].reprocess())
    session.commit()
    assert store.pending_quarantine()[0].attempts == 1
    repaired = raw({"id": 1, "name": "Benfica"})
    assert pipeline.reprocess(repaired, fingerprint).status is ResolutionStatus.MATCHED
    session.commit()
    assert store.pending_quarantine() == ()
    with pytest.raises(LookupError):
        store.resolve_quarantine("missing", NOW)


def test_fusion_persistence_and_empty_decision_candidate(session) -> None:
    store = IdentityFusionStore(session)
    observation = ProviderObservation("p", "team", {"name": "Ajax"}, NOW, "hash")
    result = DataFusionEngine(ProviderPriorityPolicy({"p": 1})).fuse(
        (observation,), NOW
    )
    store.save_fusion(result)
    unmatched = IdentityDecision(
        "p", "none", ResolutionStatus.UNMATCHED, NOW, None, "below"
    )
    store.save_decision(unmatched)
    session.commit()
    assert session.scalar(select(FusionResultRecord)).values["name"] == "Ajax"
    record = session.scalar(
        select(IdentityDecisionRecord).where(IdentityDecisionRecord.external_id == "none")
    )
    restored = IdentityFusionStore._decision(record)
    assert restored.provider == unmatched.provider
    assert restored.external_id == unmatched.external_id
    assert restored.status is unmatched.status


def test_quarantine_domain_roundtrip(session) -> None:
    store = IdentityFusionStore(session)
    item = QuarantinedData("p", "teams", "hash", "reason", NOW)
    store.quarantine(item)
    session.commit()
    assert session.scalar(select(DataQuarantineRecord)) is not None


def test_g7_migration_upgrade_and_downgrade() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "migrations"
        / "versions"
        / "9c7b7e30f003_create_identity_fusion_workflow.py"
    )
    spec = importlib.util.spec_from_file_location("g7_migration", path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    names = {"identity_decisions", "fusion_results", "data_quarantine"}
    try:
        with engine.begin() as connection:
            migration.op = Operations(MigrationContext.configure(connection))
            migration.upgrade()
            assert names <= set(connection.dialect.get_table_names(connection))
            migration.downgrade()
            assert names.isdisjoint(connection.dialect.get_table_names(connection))
    finally:
        engine.dispose()
