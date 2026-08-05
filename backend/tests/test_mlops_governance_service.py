from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.services.mlops_governance_service import MLOpsGovernanceService
from app.services.temporal_ml_service import MODEL_NAME, MODEL_VERSION
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    ModelDeploymentRecord,
    PredictiveModelRecord,
    TrainingDatasetRecord,
)


def db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    CanonicalBase.metadata.create_all(engine)
    return Session(engine)


def temporal_model(market: str, approved: bool, improvement: float) -> PredictiveModelRecord:
    return PredictiveModelRecord(
        name=MODEL_NAME,
        version=MODEL_VERSION,
        competition_id="global",
        market=market,
        parameters={
            "samples": 500,
            "dataset_checksum": f"checksum-{market}",
            "approved": approved,
            "relative_improvement": improvement,
            "improvement_confidence_interval_95": (
                [.01, .05] if improvement > 0 else [-.05, -.01]
            ),
            "test_log_loss": .61,
            "baseline_log_loss": .64,
            "validation": "chronological_70_15_15",
            "calibration": "temperature_on_holdout",
        },
    )


def deployment(family: str, role: str, name: str) -> ModelDeploymentRecord:
    return ModelDeploymentRecord(
        market_family=family,
        model_name=name,
        model_version="v1",
        role=role,
        active=True,
        weights={},
        gate={},
        created_at=datetime.now(timezone.utc),
    )


def test_governance_registers_reproducible_dataset_and_safe_canary(monkeypatch) -> None:
    db = db_session()
    db.add_all([
        temporal_model("match_winner", True, .03),
        temporal_model("over_2_5_goals", False, -.02),
        deployment("results", "champion", "specialized_champion"),
        deployment("results", "shadow", "specialized_challenger"),
        deployment("goals", "champion", "specialized_champion"),
        deployment("goals", "shadow", "specialized_challenger"),
    ])
    db.commit()
    monkeypatch.setattr(MLOpsGovernanceService, "_holdout_ablations", lambda *_: {})

    result = MLOpsGovernanceService(db).run()
    db.commit()

    dataset = db.scalar(select(TrainingDatasetRecord))
    assert dataset is not None
    assert dataset.checksum and dataset.cutoff_at
    assert dataset.feature_schema["leakage_contract"] == "feature_event_at < target_kickoff_at"
    assert result["gates"]["challenger_improves_baseline"] is True
    assert result["gates"]["reproducible_training"] is True

    deployments = db.scalars(select(ModelDeploymentRecord)).all()
    by_key = {(row.market_family, row.model_name): row for row in deployments}
    assert by_key[("results", "specialized_champion")].active is True
    assert by_key[("results", "specialized_challenger")].role == "canary"
    assert by_key[("results", "specialized_challenger")].gate["canary_traffic"] == .05
    assert by_key[("goals", "specialized_challenger")].role == "shadow"


def test_rollback_preserves_champion_and_returns_challenger_to_shadow() -> None:
    db = db_session()
    db.add_all([
        deployment("results", "champion", "specialized_champion"),
        deployment("results", "canary", "specialized_challenger"),
    ])
    db.commit()

    assert MLOpsGovernanceService(db).rollback("results") is True
    db.commit()

    rows = db.scalars(select(ModelDeploymentRecord)).all()
    champion = next(row for row in rows if row.model_name == "specialized_champion")
    challenger = next(row for row in rows if row.model_name == "specialized_challenger")
    assert champion.active is True
    assert challenger.role == "shadow"
    assert challenger.gate["rollback_at"]

