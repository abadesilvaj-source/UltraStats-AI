"""Persistência dos perfis e snapshots de portfólio."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.risk import PerformanceMetrics, PortfolioPlan, RiskProfile
from ultrastats_ai.infrastructure.database.models import (
    PortfolioSnapshotRecord,
    RiskProfileRecord,
)


class RiskPortfolioStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_profile(
        self,
        user_id: str,
        profile: RiskProfile,
        updated_at: datetime,
    ) -> RiskProfileRecord:
        if not user_id.strip():
            raise ValueError("Perfil exige usuário.")
        record = self.session.scalar(
            select(RiskProfileRecord).where(RiskProfileRecord.user_id == user_id)
        )
        limits = {
            "kelly_fraction": str(profile.kelly_fraction),
            "maximum_stake_fraction": str(profile.maximum_stake_fraction),
            "maximum_daily_fraction": str(profile.maximum_daily_fraction),
            "maximum_competition_fraction": str(profile.maximum_competition_fraction),
            "maximum_market_fraction": str(profile.maximum_market_fraction),
            "maximum_correlated_positions": profile.maximum_correlated_positions,
        }
        if record is None:
            record = RiskProfileRecord(user_id=user_id)
            self.session.add(record)
        record.kind = profile.kind.value
        record.limits = limits
        record.updated_at = updated_at
        return record

    def save_snapshot(
        self,
        user_id: str,
        plan: PortfolioPlan,
        metrics: PerformanceMetrics,
        generated_at: datetime,
    ) -> PortfolioSnapshotRecord:
        if not user_id.strip():
            raise ValueError("Snapshot exige usuário.")
        record = PortfolioSnapshotRecord(
            user_id=user_id,
            bankroll=str(plan.bankroll),
            total_exposure=str(plan.total_exposure),
            positions=[
                {
                    "recommendation_id": item.recommendation_id,
                    "competition": item.competition,
                    "market": item.market,
                    "correlation_key": item.correlation_key,
                    "stake": str(item.stake),
                    "kelly_fraction": str(item.kelly_fraction),
                }
                for item in plan.positions
            ],
            blocked={key: list(value) for key, value in plan.blocked.items()},
            metrics={
                "total_staked": str(metrics.total_staked),
                "net_profit": str(metrics.net_profit),
                "roi": str(metrics.roi),
                "yield_rate": str(metrics.yield_rate),
                "maximum_drawdown": str(metrics.maximum_drawdown),
            },
            generated_at=generated_at,
        )
        self.session.add(record)
        return record

    def history(self, user_id: str) -> tuple[PortfolioSnapshotRecord, ...]:
        return tuple(
            self.session.scalars(
                select(PortfolioSnapshotRecord)
                .where(PortfolioSnapshotRecord.user_id == user_id)
                .order_by(PortfolioSnapshotRecord.generated_at.desc())
            ).all()
        )
