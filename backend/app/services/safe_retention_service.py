from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ultrastats_ai.infrastructure.database.models import (
    BackupCatalogRecord, OddsSnapshotRecord, PaperBetRecord,
    RecommendationOpportunityRecord,
)


class SafeRetentionService:
    """Compacta apenas snapshots reconstruíveis após backup verificado."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, *, execute: bool = False) -> dict[str, object]:
        now = datetime.now(timezone.utc)
        odds_cutoff = now - timedelta(days=int(os.getenv("ODDS_SNAPSHOT_RETENTION_DAYS", "180")))
        recommendation_cutoff = now - timedelta(days=int(os.getenv("RECOMMENDATION_RETENTION_DAYS", "365")))
        protected = select(PaperBetRecord.opportunity_id)
        old_recommendations = select(RecommendationOpportunityRecord.id).where(
            RecommendationOpportunityRecord.evaluated_at < recommendation_cutoff,
            RecommendationOpportunityRecord.id.not_in(protected),
        ).limit(int(os.getenv("RETENTION_DELETE_BATCH_SIZE", "10000")))
        old_odds = select(OddsSnapshotRecord.id).where(
            OddsSnapshotRecord.captured_at < odds_cutoff
        ).limit(int(os.getenv("RETENTION_DELETE_BATCH_SIZE", "10000")))
        recommendation_ids = list(self.session.scalars(old_recommendations))
        odds_ids = list(self.session.scalars(old_odds))
        verified = self.session.scalar(
            select(BackupCatalogRecord.id).where(
                BackupCatalogRecord.status == "verified",
                BackupCatalogRecord.verified_at >= now - timedelta(days=7),
            ).limit(1)
        )
        enabled = os.getenv("DATA_RETENTION_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
        performed = bool(execute and enabled and verified)
        if performed:
            if recommendation_ids:
                self.session.execute(delete(RecommendationOpportunityRecord).where(RecommendationOpportunityRecord.id.in_(recommendation_ids)))
            if odds_ids:
                self.session.execute(delete(OddsSnapshotRecord).where(OddsSnapshotRecord.id.in_(odds_ids)))
            self.session.commit()
        return {
            "performed": performed, "backup_verified": bool(verified),
            "recommendation_candidates": len(recommendation_ids),
            "odds_snapshot_candidates": len(odds_ids),
            "reason": None if performed else "disabled_or_no_recent_verified_backup",
        }
