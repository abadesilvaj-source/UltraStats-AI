"""Registry, forecasts imutáveis e backtests persistentes."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.prediction import BacktestResult, ModelSpecification, ProbabilisticForecast
from ultrastats_ai.infrastructure.database.models import (
    ModelBacktestRecord,
    PredictiveForecastRecord,
    PredictiveModelRecord,
)


def _strings(values):
    return {key: str(value) for key, value in values.items()}


class PredictiveModelStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def register(self, specification: ModelSpecification) -> bool:
        exists = self.session.scalar(
            select(PredictiveModelRecord.id).where(
                PredictiveModelRecord.name == specification.name,
                PredictiveModelRecord.version == specification.version,
                PredictiveModelRecord.competition_id == specification.competition_id,
                PredictiveModelRecord.market == specification.market,
            )
        )
        if exists is not None:
            return False
        self.session.add(
            PredictiveModelRecord(
                name=specification.name,
                version=specification.version,
                competition_id=specification.competition_id,
                market=specification.market,
                parameters=_strings(specification.parameters),
            )
        )
        return True

    def save_forecast(
        self,
        match_id: str,
        forecast: ProbabilisticForecast,
        generated_at: datetime,
    ) -> None:
        exists = self.session.scalar(
            select(PredictiveForecastRecord.id).where(
                PredictiveForecastRecord.match_id == match_id,
                PredictiveForecastRecord.model_name == forecast.model_name,
                PredictiveForecastRecord.model_version == forecast.model_version,
                PredictiveForecastRecord.market == forecast.market,
            )
        )
        if exists is not None:
            raise ValueError("Forecast publicado é imutável.")
        self.session.add(
            PredictiveForecastRecord(
                match_id=match_id,
                model_name=forecast.model_name,
                model_version=forecast.model_version,
                market=forecast.market,
                probabilities=_strings(forecast.probabilities),
                explanations=_strings(forecast.explanations),
                generated_at=generated_at,
            )
        )

    def save_backtest(
        self,
        model_name: str,
        model_version: str,
        result: BacktestResult,
        evaluated_at: datetime,
    ) -> None:
        self.session.add(
            ModelBacktestRecord(
                model_name=model_name,
                model_version=model_version,
                samples=result.samples,
                metrics={
                    "brier_score": str(result.brier_score),
                    "log_loss": str(result.log_loss),
                    "accuracy": str(result.accuracy),
                    "calibration_error": str(result.calibration_error),
                },
                evaluated_at=evaluated_at,
            )
        )

    def comparison(self) -> tuple[dict[str, object], ...]:
        records = self.session.scalars(
            select(ModelBacktestRecord).order_by(ModelBacktestRecord.evaluated_at.desc())
        ).all()
        return tuple(
            {
                "model_name": record.model_name,
                "model_version": record.model_version,
                "samples": record.samples,
                **record.metrics,
            }
            for record in records
        )
