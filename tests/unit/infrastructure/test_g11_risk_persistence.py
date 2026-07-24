from datetime import datetime, timezone
from decimal import Decimal as D
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.risk import (
    BetCandidate,
    PerformanceMetrics,
    RiskPortfolioEngine,
    RiskProfile,
    RiskProfileKind,
)
from ultrastats_ai.infrastructure.database.models import CanonicalBase, RiskProfileRecord
from ultrastats_ai.infrastructure.risk import RiskPortfolioStore


NOW = datetime.now(timezone.utc)


def test_profile_upsert_snapshot_and_history() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            store = RiskPortfolioStore(session)
            conservative = RiskProfile.preset(RiskProfileKind.CONSERVATIVE)
            store.save_profile("user", conservative, NOW)
            session.flush()
            moderate = RiskProfile.preset(RiskProfileKind.MODERATE)
            store.save_profile("user", moderate, NOW)
            plan = RiskPortfolioEngine(moderate).optimize(
                D("1000"),
                (BetCandidate("r", "league", "1x2", "match", D(".6"), D("2"), D(".8")),),
            )
            metrics = PerformanceMetrics(D("20"), D("5"), D(".005"), D(".25"), D(".02"))
            snapshot = store.save_snapshot("user", plan, metrics, NOW)
            session.commit()
            assert session.scalar(select(RiskProfileRecord)).kind == "moderate"
            assert snapshot.positions[0]["stake"] == "20.00"
            assert store.history("user") == (snapshot,)
            assert store.history("other") == ()
    finally:
        engine.dispose()


def test_store_requires_user() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            store = RiskPortfolioStore(session)
            profile = RiskProfile.preset(RiskProfileKind.MODERATE)
            with pytest.raises(ValueError, match="usuário"):
                store.save_profile("", profile, NOW)
            plan = RiskPortfolioEngine(profile).optimize(D("1000"), ())
            metrics = PerformanceMetrics(D("0"), D("0"), D("0"), D("0"), D("0"))
            with pytest.raises(ValueError, match="usuário"):
                store.save_snapshot("", plan, metrics, NOW)
    finally:
        engine.dispose()


def test_g11_migration_upgrade_and_downgrade() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "migrations"
        / "versions"
        / "d4bf1261d117_create_risk_portfolio.py"
    )
    spec = importlib.util.spec_from_file_location("g11_migration", path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    names = {"risk_profiles", "portfolio_snapshots"}
    try:
        with engine.begin() as connection:
            migration.op = Operations(MigrationContext.configure(connection))
            migration.upgrade()
            assert names <= set(connection.dialect.get_table_names(connection))
            migration.downgrade()
            assert names.isdisjoint(connection.dialect.get_table_names(connection))
    finally:
        engine.dispose()
