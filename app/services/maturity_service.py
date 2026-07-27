from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Match, MatchStatistics, Odd, Prediction
from ultrastats_ai.infrastructure.database.models import (
    IdentityDecisionRecord,
    LiveSnapshotRecord,
    OperationalAlertRecord,
    OperationalMetricRecord,
    ProviderHealthRecord,
    RawProviderPayloadRecord,
)


class MaturityService:
    """Mede SLA operacional sem confundi-lo com cobertura bruta."""

    providers = (
        "api_football",
        "football_data",
        "football_data_uk",
        "openligadb",
        "sportmonks",
        "statsbomb_open_data",
        "the_odds_api",
        "thesportsdb",
    )
    capabilities = {
        "api_football": ("fixtures", "statistics", "odds", "lineups", "live"),
        "football_data": ("fixtures", "scores"),
        "football_data_uk": ("fixtures", "odds"),
        "openligadb": ("fixtures", "scores"),
        "sportmonks": ("fixtures", "statistics", "lineups", "live"),
        "statsbomb_open_data": ("historical_statistics", "lineups"),
        "the_odds_api": ("odds",),
        "thesportsdb": ("fixtures", "scores"),
    }

    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self) -> dict[str, object]:
        report = self.report()
        now = datetime.now(timezone.utc)
        for name, value in (
            ("data_quality_score", report["quality_score"]),
            ("raw_statistics_coverage", report["raw_coverage"]["statistics"]),
            ("eligible_statistics_coverage", report["coverage"]["statistics"]),
            ("lineup_coverage", report["coverage"]["lineups"]),
            ("odds_coverage", report["coverage"]["odds"]),
        ):
            self.session.add(OperationalMetricRecord(
                name=name,
                value=f"{float(value):.6f}",
                labels={"scope": "provider_neutral_sla"},
                recorded_at=now,
            ))
        for alert in report["alerts"]:
            existing = self.session.scalar(
                select(OperationalAlertRecord).where(
                    OperationalAlertRecord.code == alert["code"],
                    OperationalAlertRecord.status == "open",
                )
            )
            if existing is None:
                self.session.add(OperationalAlertRecord(
                    code=alert["code"],
                    severity=alert["severity"],
                    message=alert["message"],
                    status="open",
                    created_at=now,
                ))
        return report

    def report(self) -> dict[str, object]:
        now = datetime.now(timezone.utc)
        naive = now.replace(tzinfo=None)
        active = self.session.scalars(select(Match).where(
            Match.status.in_(("scheduled", "not_started", "in_progress")),
            Match.kickoff_at >= naive - timedelta(hours=2),
            Match.kickoff_at <= naive + timedelta(days=14),
        )).all()
        finished = self.session.scalars(select(Match).where(
            Match.status == "finished",
            Match.kickoff_at >= naive - timedelta(days=14),
        )).all()
        active_ids = [item.id for item in active] or [-1]
        finished_ids = [item.id for item in finished] or [-1]
        stats_ids = set(self.session.scalars(
            select(MatchStatistics.match_id).where(
                MatchStatistics.match_id.in_(finished_ids)
            )
        ).all())
        odds_ids = set(self.session.scalars(
            select(Odd.match_id).where(Odd.match_id.in_(active_ids)).distinct()
        ).all())
        prediction_ids = set(self.session.scalars(
            select(Prediction.match_id)
            .where(Prediction.match_id.in_(active_ids)).distinct()
        ).all())

        identities = self.session.scalars(select(IdentityDecisionRecord).where(
            IdentityDecisionRecord.status == "matched",
            IdentityDecisionRecord.candidate_id.in_(
                [f"match:{item.id}" for item in active + finished] or ["-1"]
            ),
        )).all()
        providers_by_match: dict[int, set[str]] = {}
        for row in identities:
            try:
                match_id = int(row.candidate_id.removeprefix("match:"))
            except (TypeError, ValueError):
                continue
            providers_by_match.setdefault(match_id, set()).add(row.provider)
        for item in active + finished:
            if item.source and item.external_id:
                providers_by_match.setdefault(item.id, set()).add(item.source)

        stats_eligible = {
            item.id for item in finished
            if providers_by_match.get(item.id, set())
            & {"api_football", "sportmonks"}
        }
        odds_eligible = {
            item.id for item in active
            if providers_by_match.get(item.id, set())
            & {"api_football", "football_data_uk", "the_odds_api"}
        }
        lineup_window = [
            item for item in active
            if naive - timedelta(minutes=30)
            <= self._as_naive(item.kickoff_at)
            <= naive + timedelta(minutes=120)
            and providers_by_match.get(item.id, set())
            & {"api_football", "sportmonks"}
        ]
        lineup_ids = self._lineup_match_ids(lineup_window, now)

        raw = {
            "statistics": self._ratio(len(stats_ids), len(finished)),
            "odds": self._ratio(len(odds_ids), len(active)),
            "predictions": self._ratio(len(prediction_ids), len(active)),
            "lineups": self._ratio(len(lineup_ids), len(active)),
        }
        coverage = {
            "statistics": self._ratio(
                len(stats_ids & stats_eligible), len(stats_eligible)
            ),
            "odds": self._ratio(
                len(odds_ids & odds_eligible), len(odds_eligible)
            ),
            "predictions": self._ratio(len(prediction_ids), len(active)),
            "lineups": self._ratio(len(lineup_ids), len(lineup_window)),
        }

        latest_odds = self.session.scalar(select(func.max(Odd.collected_at)))
        odds_fresh = bool(
            latest_odds
            and latest_odds >= naive - timedelta(hours=6)
        )
        in_progress = [item for item in active if item.status == "in_progress"]
        latest_live = self.session.scalar(
            select(func.max(LiveSnapshotRecord.captured_at))
        )
        live_fresh = not in_progress or bool(
            latest_live
            and self._as_aware(latest_live) >= now - timedelta(minutes=5)
        )
        provider_status = self._provider_status(now)
        checked = [item for item in provider_status.values() if item["checked"]]
        availability = self._ratio(
            sum(bool(item["available"]) for item in checked), len(checked)
        ) if checked else 0.0
        multi_source = self._ratio(
            sum(len(providers_by_match.get(item.id, set())) >= 2 for item in active),
            len(active),
        )
        stats_fresh = bool(self.session.scalar(
            select(func.max(RawProviderPayloadRecord.collected_at)).where(
                RawProviderPayloadRecord.resource.in_(
                    ("statistics", "statistics_attempt")
                )
            )
        ))
        quality = round(
            coverage["statistics"] * .25
            + coverage["odds"] * .20
            + coverage["predictions"] * .20
            + coverage["lineups"] * .10
            + float(stats_fresh and odds_fresh) * .10
            + float(live_fresh) * .05
            + availability * .05
            + multi_source * .05,
            4,
        )
        alerts: list[dict[str, str]] = []
        for code, value, threshold, message in (
            ("statistics_sla_low", coverage["statistics"], .90,
             "Cobertura estatística elegível abaixo de 90%."),
            ("odds_sla_low", coverage["odds"], .90,
             "Cobertura de odds elegível abaixo de 90%."),
            ("prediction_sla_low", coverage["predictions"], .90,
             "Cobertura de previsões abaixo de 90%."),
        ):
            if value < threshold:
                alerts.append({
                    "code": code, "severity": "warning", "message": message
                })
        if not odds_fresh and odds_eligible:
            alerts.append({
                "code": "odds_stale", "severity": "critical",
                "message": "As odds elegíveis possuem mais de seis horas.",
            })
        if not live_fresh:
            alerts.append({
                "code": "live_feed_stale", "severity": "critical",
                "message": "Há partidas ao vivo sem snapshot há cinco minutos.",
            })
        return {
            "quality_score": quality,
            "score_definition": "operational_sla",
            "window_days": 14,
            "matches": {
                "active": len(active), "finished": len(finished),
                "statistics_eligible": len(stats_eligible),
                "odds_eligible": len(odds_eligible),
                "lineups_eligible": len(lineup_window),
            },
            "coverage": coverage,
            "raw_coverage": raw,
            "freshness": {
                "latest_odds": latest_odds.isoformat() if latest_odds else None,
                "odds_stale": not odds_fresh,
                "latest_live": latest_live.isoformat() if latest_live else None,
                "live_stale": not live_fresh,
            },
            "neutrality": {
                "base_weight": 1.0,
                "decision": "field_consensus_then_recency",
                "multi_provider_identity_coverage": multi_source,
                "capabilities": self.capabilities,
            },
            "providers": provider_status,
            "alerts": alerts,
        }

    def _lineup_match_ids(
        self, matches: list[Match], now: datetime
    ) -> set[int]:
        result: set[int] = set()
        for match in matches:
            identities = self.session.scalars(
                select(IdentityDecisionRecord).where(
                    IdentityDecisionRecord.candidate_id == f"match:{match.id}",
                    IdentityDecisionRecord.status == "matched",
                    IdentityDecisionRecord.provider.in_(
                        ("api_football", "sportmonks")
                    ),
                )
            ).all()
            candidates = {
                (
                    row.provider,
                    row.external_id.removeprefix("match:"),
                )
                for row in identities
            }
            if match.source in {"api_football", "sportmonks"}:
                candidates.add((match.source, str(match.external_id)))
            for provider, external_id in candidates:
                found = self.session.scalar(select(RawProviderPayloadRecord.id).where(
                    RawProviderPayloadRecord.provider == provider,
                    RawProviderPayloadRecord.resource == "lineups",
                    RawProviderPayloadRecord.external_id.like(
                        f"{external_id}%"
                    ),
                    RawProviderPayloadRecord.collected_at
                    >= now - timedelta(days=2),
                ).limit(1))
                if found:
                    result.add(match.id)
                    break
        return result

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
            checked = bool(health or last_payload)
            result[provider] = {
                "checked": checked,
                "available": bool(
                    checked
                    and (
                        health is None
                        or (
                            health.available
                            and self._as_aware(health.checked_at)
                            >= now - timedelta(hours=6)
                        )
                    )
                ),
                "latency_ms": health.latency_ms if health else None,
                "checked_at": health.checked_at.isoformat() if health else None,
                "last_payload_at": (
                    last_payload.isoformat() if last_payload else None
                ),
                "capabilities": self.capabilities.get(provider, ()),
                "base_weight": 1.0,
            }
        return result

    @staticmethod
    def _ratio(numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 4) if denominator else 1.0

    @staticmethod
    def _as_aware(value: datetime) -> datetime:
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value

    @staticmethod
    def _as_naive(value: datetime) -> datetime:
        return (
            value.astimezone(timezone.utc).replace(tzinfo=None)
            if value.tzinfo is not None else value
        )
