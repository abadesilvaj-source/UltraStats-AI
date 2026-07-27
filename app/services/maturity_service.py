from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Match, MatchStatistics, Odd, Prediction
from ultrastats_ai.infrastructure.database.models import (
    LiveSnapshotRecord,
    OperationalAlertRecord,
    OperationalMetricRecord,
    ProviderHealthRecord,
    RawProviderPayloadRecord,
)


class MaturityService:
    """Mede qualidade, atualidade e cobertura do ciclo operacional."""

    providers = (
        "api_football",
        "football_data_org",
        "football_data_uk",
        "openligadb",
        "sportmonks",
        "statsbomb_open_data",
        "the_odds_api",
        "thesportsdb",
    )

    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self) -> dict[str, object]:
        report = self.report()
        now = datetime.now(timezone.utc)
        for name, value in (
            ("data_quality_score", report["quality_score"]),
            ("statistics_coverage", report["coverage"]["statistics"]),
            ("lineup_coverage", report["coverage"]["lineups"]),
            ("odds_coverage", report["coverage"]["odds"]),
        ):
            self.session.add(
                OperationalMetricRecord(
                    name=name,
                    value=f"{float(value):.6f}",
                    labels={"scope": "rolling_14_days"},
                    recorded_at=now,
                )
            )
        for alert in report["alerts"]:
            existing = self.session.scalar(
                select(OperationalAlertRecord).where(
                    OperationalAlertRecord.code == alert["code"],
                    OperationalAlertRecord.status == "open",
                )
            )
            if existing is None:
                self.session.add(
                    OperationalAlertRecord(
                        code=alert["code"],
                        severity=alert["severity"],
                        message=alert["message"],
                        status="open",
                        created_at=now,
                    )
                )
        return report

    def report(self) -> dict[str, object]:
        now = datetime.now(timezone.utc)
        now_naive = now.replace(tzinfo=None)
        window = now_naive - timedelta(days=14)
        active = self.session.scalars(
            select(Match).where(
                Match.status.in_(("scheduled", "not_started", "in_progress")),
                Match.kickoff_at >= now_naive - timedelta(hours=2),
                Match.kickoff_at <= now_naive + timedelta(days=14),
            )
        ).all()
        finished = self.session.scalars(
            select(Match).where(
                Match.status == "finished",
                Match.kickoff_at >= window,
            )
        ).all()
        statistics_matches = set(
            self.session.scalars(
                select(MatchStatistics.match_id).where(
                    MatchStatistics.match_id.in_(
                        [item.id for item in finished] or [-1]
                    )
                )
            ).all()
        )
        odds_matches = set(
            self.session.scalars(
                select(Odd.match_id)
                .where(Odd.match_id.in_([item.id for item in active] or [-1]))
                .distinct()
            ).all()
        )
        prediction_matches = set(
            self.session.scalars(
                select(Prediction.match_id)
                .where(
                    Prediction.match_id.in_([item.id for item in active] or [-1])
                )
                .distinct()
            ).all()
        )
        lineup_fixture_ids = {
            str(value).split(":", 1)[0]
            for value in self.session.scalars(
                select(RawProviderPayloadRecord.external_id).where(
                    RawProviderPayloadRecord.resource == "lineups",
                    RawProviderPayloadRecord.collected_at
                    >= now - timedelta(days=14),
                )
            ).all()
            if value
        }
        active_external_ids = {
            str(item.external_id) for item in active if item.external_id
        }
        lineup_matches = active_external_ids.intersection(lineup_fixture_ids)
        stats_coverage = self._ratio(len(statistics_matches), len(finished))
        odds_coverage = self._ratio(len(odds_matches), len(active))
        prediction_coverage = self._ratio(
            len(prediction_matches), len(active)
        )
        lineup_coverage = self._ratio(len(lineup_matches), len(active))
        latest_odds = self.session.scalar(select(func.max(Odd.collected_at)))
        odds_stale = bool(
            latest_odds
            and latest_odds < now_naive - timedelta(hours=6)
        )
        latest_live = self.session.scalar(
            select(func.max(LiveSnapshotRecord.captured_at))
        )
        live_stale = bool(
            latest_live
            and self._as_aware(latest_live)
            < now - timedelta(minutes=5)
        )
        provider_status = self._provider_status(now)
        quality_score = round(
            (
                stats_coverage * 0.30
                + odds_coverage * 0.25
                + prediction_coverage * 0.20
                + lineup_coverage * 0.15
                + self._ratio(
                    sum(
                        bool(item["available"])
                        for item in provider_status.values()
                    ),
                    len(provider_status),
                )
                * 0.10
            ),
            4,
        )
        alerts: list[dict[str, str]] = []
        if stats_coverage < 0.70:
            alerts.append({
                "code": "statistics_coverage_low",
                "severity": "warning",
                "message": "Cobertura pós-jogo abaixo de 70%.",
            })
        if odds_coverage < 0.60:
            alerts.append({
                "code": "odds_coverage_low",
                "severity": "warning",
                "message": "Cobertura de odds abaixo de 60%.",
            })
        if lineup_coverage < 0.50:
            alerts.append({
                "code": "lineup_coverage_low",
                "severity": "info",
                "message": "Menos de 50% das partidas possuem escalações.",
            })
        if odds_stale:
            alerts.append({
                "code": "odds_stale",
                "severity": "critical",
                "message": "As odds mais recentes possuem mais de seis horas.",
            })
        if live_stale:
            alerts.append({
                "code": "live_feed_stale",
                "severity": "critical",
                "message": "O feed ao vivo não recebe snapshot há cinco minutos.",
            })
        return {
            "quality_score": quality_score,
            "window_days": 14,
            "matches": {
                "active": len(active),
                "finished": len(finished),
            },
            "coverage": {
                "statistics": stats_coverage,
                "odds": odds_coverage,
                "predictions": prediction_coverage,
                "lineups": lineup_coverage,
            },
            "freshness": {
                "latest_odds": latest_odds.isoformat()
                if latest_odds else None,
                "odds_stale": odds_stale,
                "latest_live": latest_live.isoformat()
                if latest_live else None,
                "live_stale": live_stale,
            },
            "providers": provider_status,
            "alerts": alerts,
        }

    def _provider_status(
        self, now: datetime
    ) -> dict[str, dict[str, object]]:
        result: dict[str, dict[str, object]] = {}
        for provider in self.providers:
            health = self.session.scalar(
                select(ProviderHealthRecord)
                .where(ProviderHealthRecord.provider == provider)
                .order_by(ProviderHealthRecord.checked_at.desc())
            )
            last_payload = self.session.scalar(
                select(func.max(RawProviderPayloadRecord.collected_at)).where(
                    RawProviderPayloadRecord.provider == provider
                )
            )
            result[provider] = {
                "available": bool(
                    health
                    and health.available
                    and self._as_aware(health.checked_at)
                    >= now - timedelta(hours=6)
                ),
                "latency_ms": health.latency_ms if health else None,
                "checked_at": health.checked_at.isoformat()
                if health else None,
                "last_payload_at": last_payload.isoformat()
                if last_payload else None,
            }
        return result

    @staticmethod
    def _ratio(numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 4) if denominator else 0.0

    @staticmethod
    def _as_aware(value: datetime) -> datetime:
        return (
            value.replace(tzinfo=timezone.utc)
            if value.tzinfo is None else value
        )
