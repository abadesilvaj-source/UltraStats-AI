"""Executa todo o pipeline local de treinamento e materialização preditiva."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import func, select

from app.database.session import SessionLocal
from app.models import Audit, Match, Prediction
from app.services.operational_intelligence_service import (
    OperationalIntelligenceService,
)
from app.services.operational_pipeline_service import OperationalPipelineService
from app.services.temporal_ml_service import TemporalMLService
from ultrastats_ai.infrastructure.database.models import (
    DecisionPolicyRecord,
    ModelValidationRecord,
    PredictiveModelRecord,
    TemporalBacktestRecord,
)


def emit(stage: str, **payload: object) -> None:
    print(json.dumps({
        "at": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        **payload,
    }, ensure_ascii=False, default=str), flush=True)


def main() -> None:
    session = SessionLocal()
    try:
        emit("inventory", **{
            "finished_matches": session.scalar(
                select(func.count()).select_from(Match).where(
                    Match.status == "finished"
                )
            ) or 0,
            "predictions": session.scalar(
                select(func.count()).select_from(Prediction)
            ) or 0,
            "audits": session.scalar(
                select(func.count()).select_from(Audit)
            ) or 0,
        })

        emit("temporal_training_started")
        temporal = TemporalMLService(
            session,
            allow_training=True,
            force_retraining=True,
        )._load_or_train()
        session.commit()
        emit("temporal_training_completed", models={
            market: {
                "approved": values.get("approved"),
                "samples": values.get("samples"),
                "test_log_loss": values.get("test_log_loss"),
                "baseline_log_loss": values.get("baseline_log_loss"),
                "test_accuracy": values.get("test_accuracy"),
            }
            for market, values in temporal.items()
        })

        emit("prediction_refresh_started")
        predictions = OperationalPipelineService(
            session, temporal_ml_training=False
        ).refresh_all_predictions()
        session.commit()
        emit("prediction_refresh_completed", persisted=predictions)

        emit("operational_training_started")
        operational = OperationalIntelligenceService(session).run()
        session.commit()
        emit("operational_training_completed", result=operational)

        summary = {
            "models": session.scalar(
                select(func.count()).select_from(PredictiveModelRecord)
            ) or 0,
            "validations": session.scalar(
                select(func.count()).select_from(ModelValidationRecord)
            ) or 0,
            "temporal_backtests": session.scalar(
                select(func.count()).select_from(TemporalBacktestRecord)
            ) or 0,
            "decision_policies": session.scalar(
                select(func.count()).select_from(DecisionPolicyRecord)
            ) or 0,
        }
        emit("all_training_completed", **summary)
    except Exception as error:
        session.rollback()
        emit("training_failed", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
