from datetime import datetime, timezone
from decimal import Decimal as D
import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.prediction import (
    BacktestResult,
    ModelSpecification,
    ProbabilisticForecast,
)
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    ModelBacktestRecord,
    PredictiveForecastRecord,
    PredictiveModelRecord,
)
from ultrastats_ai.infrastructure.prediction import PredictiveModelStore


NOW = datetime.now(timezone.utc)


def test_registry_immutable_forecast_and_comparison() -> None:
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            store = PredictiveModelStore(session)
            specification = ModelSpecification("model", "1", "league", "1x2", {"a": D("1")})
            assert store.register(specification)
            session.commit()
            assert not store.register(specification)
            assert session.scalar(select(PredictiveModelRecord)).parameters == {"a": "1"}
            forecast = ProbabilisticForecast(
                "model", "1", "1x2", {"home": D(".6"), "away": D(".4")}, {"xg": D("1.2")}
            )
            store.save_forecast("match", forecast, NOW)
            session.commit()
            with pytest.raises(ValueError, match="imutável"):
                store.save_forecast("match", forecast, NOW)
            assert session.scalar(select(PredictiveForecastRecord)).probabilities["home"] == "0.6"
            result = BacktestResult(10, D(".2"), D(".4"), D(".7"), D(".1"))
            store.save_backtest("model", "1", result, NOW)
            session.commit()
            comparison = store.comparison()
            assert comparison[0]["accuracy"] == "0.7"
            assert session.scalar(select(ModelBacktestRecord)).samples == 10
    finally:
        engine.dispose()


def test_g9_migration_upgrade_and_downgrade() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "migrations"
        / "versions"
        / "b29d9040b005_create_predictive_registry.py"
    )
    spec = importlib.util.spec_from_file_location("g9_migration", path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    names = {"predictive_models", "predictive_forecasts", "model_backtests"}
    try:
        with engine.begin() as connection:
            migration.op = Operations(MigrationContext.configure(connection))
            migration.upgrade()
            assert names <= set(connection.dialect.get_table_names(connection))
            migration.downgrade()
            assert names.isdisjoint(connection.dialect.get_table_names(connection))
    finally:
        engine.dispose()
