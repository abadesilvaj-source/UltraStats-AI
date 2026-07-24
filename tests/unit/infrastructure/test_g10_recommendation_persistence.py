from datetime import datetime, timezone
from decimal import Decimal as D
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.recommendation import OddsQuote, OpportunityInput, RecommendationEngine
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    RecommendationAuditRecord,
    RecommendationOpportunityRecord,
)
from ultrastats_ai.infrastructure.recommendation import RecommendationStore


NOW = datetime.now(timezone.utc)


def opportunity():
    quote = OddsQuote("book", D("2"), NOW)
    item = OpportunityInput("match", "1x2", "home", D(".6"), D(".9"), D(".9"), (quote,), "match")
    return RecommendationEngine().evaluate(item, NOW)


def test_history_and_audit() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            store = RecommendationStore(session)
            record = store.save(opportunity())
            session.flush()
            with pytest.raises(ValueError, match="Auditoria"):
                store.audit(record.id, "", "operator", "reason", NOW)
            store.audit(record.id, "published", "operator", "approved", NOW)
            session.commit()
            history = store.safe_history()
            assert history[0]["bookmaker"] == "book"
            assert session.scalar(select(RecommendationOpportunityRecord)).safe
            assert session.scalar(select(RecommendationAuditRecord)).action == "published"
    finally:
        engine.dispose()


def test_unsafe_metrics_preserve_null_values() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            item = OpportunityInput("match", "1x2", "home", D("0"), D(".9"), D(".9"), (), "match")
            record = RecommendationStore(session).save(RecommendationEngine().evaluate(item, NOW))
            session.flush()
            assert record.metrics["fair_odds"] is None
            assert record.metrics["expected_value"] is None
            assert RecommendationStore(session).safe_history() == ()
    finally:
        engine.dispose()


def test_g10_migration_upgrade_and_downgrade() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "migrations"
        / "versions"
        / "c3ae0150c006_create_recommendation_engine.py"
    )
    spec = importlib.util.spec_from_file_location("g10_migration", path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    names = {"recommendation_opportunities", "recommendation_audit"}
    try:
        with engine.begin() as connection:
            migration.op = Operations(MigrationContext.configure(connection))
            migration.upgrade()
            assert names <= set(connection.dialect.get_table_names(connection))
            migration.downgrade()
            assert names.isdisjoint(connection.dialect.get_table_names(connection))
    finally:
        engine.dispose()
