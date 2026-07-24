"""Histórico imutável e auditoria das recomendações."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.recommendation import Opportunity
from ultrastats_ai.infrastructure.database.models import (
    RecommendationAuditRecord,
    RecommendationOpportunityRecord,
)


class RecommendationStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, opportunity: Opportunity) -> RecommendationOpportunityRecord:
        def serialized(value):
            return str(value) if value is not None else None

        record = RecommendationOpportunityRecord(
            match_id=opportunity.match_id,
            market=opportunity.market,
            selection=opportunity.selection,
            bookmaker=opportunity.bookmaker,
            offered_odds=str(opportunity.offered_odds) if opportunity.offered_odds is not None else None,
            metrics={
                "implied_probability": serialized(opportunity.implied_probability),
                "model_probability": serialized(opportunity.model_probability),
                "fair_odds": serialized(opportunity.fair_odds),
                "expected_value": serialized(opportunity.expected_value),
                "edge": serialized(opportunity.edge),
                "confidence": serialized(opportunity.confidence),
            },
            risk=opportunity.risk.value,
            score=str(opportunity.score),
            safe=opportunity.safe,
            blocked_reasons=list(opportunity.blocked_reasons),
            explanation=list(opportunity.explanation),
            correlation_key=opportunity.correlation_key,
            evaluated_at=opportunity.evaluated_at,
        )
        self.session.add(record)
        return record

    def audit(
        self,
        opportunity_id,
        action: str,
        actor: str,
        reason: str,
        occurred_at: datetime,
    ) -> None:
        if not all((action.strip(), actor.strip(), reason.strip())):
            raise ValueError("Auditoria exige ação, responsável e motivo.")
        self.session.add(
            RecommendationAuditRecord(
                opportunity_id=opportunity_id,
                action=action,
                actor=actor,
                reason=reason,
                occurred_at=occurred_at,
            )
        )

    def safe_history(self) -> tuple[dict[str, object], ...]:
        records = self.session.scalars(
            select(RecommendationOpportunityRecord)
            .where(RecommendationOpportunityRecord.safe.is_(True))
            .order_by(RecommendationOpportunityRecord.evaluated_at.desc())
        ).all()
        return tuple(
            {
                "id": record.id,
                "match_id": record.match_id,
                "market": record.market,
                "selection": record.selection,
                "bookmaker": record.bookmaker,
                "odds": record.offered_odds,
                "score": record.score,
                "risk": record.risk,
                "evaluated_at": record.evaluated_at,
            }
            for record in records
        )
