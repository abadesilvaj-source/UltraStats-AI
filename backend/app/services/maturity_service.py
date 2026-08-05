from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.competition_catalog import (
    competition_is_modeled,
    competition_metadata,
    competition_policy,
)
from app.core.config import settings
from app.services.competition_promotion_service import (
    CompetitionPromotionService,
)
from app.models import Competition, Match, MatchStatistics, Odd, Prediction
from ultrastats_ai.infrastructure.database.models import (
    IdentityDecisionRecord,
    DataQuarantineRecord,
    FusionResultRecord,
    LiveSnapshotRecord,
    OperationalAlertRecord,
    OperationalMetricRecord,
    OddsSnapshotRecord,
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
        "goal_api",
        "zafronix",
    )
    capabilities = {
        "api_football": (
            "fixtures", "statistics", "odds", "lineups", "live",
            "events", "injuries", "player_statistics",
            "team_statistics", "provider_predictions", "live_odds",
        ),
        "football_data": ("fixtures", "scores"),
        "football_data_uk": ("fixtures", "odds"),
        "openligadb": ("fixtures", "scores"),
        "sportmonks": ("fixtures", "statistics", "lineups", "live"),
        "statsbomb_open_data": ("historical_events", "xg"),
        "the_odds_api": ("odds",),
        "thesportsdb": ("fixtures", "scores"),
        "goal_api": ("fixtures", "live", "scores", "venues"),
        "zafronix": ("fixtures", "live", "scores"),
    }
    _cached_report: dict[str, object] | None = None
    _cached_at: datetime | None = None

    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self) -> dict[str, object]:
        promotion = CompetitionPromotionService(self.session).evaluate()
        report = self.report()
        report["competition_promotion"] = promotion
        now = datetime.now(timezone.utc)
        active_alert_codes = {
            str(alert["code"]) for alert in report["alerts"]
        }
        open_alerts = self.session.scalars(
            select(OperationalAlertRecord).where(
                OperationalAlertRecord.status == "open"
            )
        ).all()
        for alert in open_alerts:
            if alert.code not in active_alert_codes:
                alert.status = "resolved"
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
        for capability, numerator_key, denominator_key in (
            ("statistics", "statistics_eligible_covered", "statistics_eligible"),
            ("odds", "odds_eligible_covered", "odds_eligible"),
            ("predictions", "predictions_eligible_covered", "predictions_eligible"),
            ("lineups", "lineups_eligible_covered", "lineups_eligible"),
        ):
            for measure, key in (("numerator", numerator_key), ("denominator", denominator_key)):
                self.session.add(OperationalMetricRecord(
                    name="coverage_contract_count", value=str(report["matches"].get(key, 0)),
                    labels={"definition_version": "g36-v1", "capability": capability,
                            "measure": measure, "window_days": "14"}, recorded_at=now,
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
        cache_seconds = max(15, int(os.getenv("MATURITY_REPORT_CACHE_SECONDS", "60")))
        cache_enabled = self.session.get_bind().dialect.name != "sqlite"
        if (
            cache_enabled
            and self.__class__._cached_report is not None
            and self.__class__._cached_at is not None
            and now - self.__class__._cached_at < timedelta(seconds=cache_seconds)
        ):
            return deepcopy(self.__class__._cached_report)
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
        competitions = {
            item.id: item
            for item in self.session.scalars(
                select(Competition).where(
                    Competition.id.in_(
                        {
                            match.competition_id
                            for match in active + finished
                        } or {-1}
                    )
                )
            ).all()
        }
        prediction_eligible = {
            item.id
            for item in active
            if (
                (competition := competitions.get(item.competition_id))
                and competition_is_modeled(competition)
            )
        }
        stats_ids = set(self.session.scalars(
            select(MatchStatistics.match_id).where(
                MatchStatistics.match_id.in_(finished_ids)
            )
        ).all())
        odds_ids = set(self.session.scalars(
            select(Odd.match_id).where(
                Odd.match_id.in_(active_ids),
                Odd.collected_at >= naive - timedelta(hours=8),
            ).distinct()
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
        provider_ids_by_match: dict[int, dict[str, str]] = {}
        for row in identities:
            try:
                match_id = int(row.candidate_id.removeprefix("match:"))
            except (TypeError, ValueError):
                continue
            providers_by_match.setdefault(match_id, set()).add(row.provider)
            provider_ids_by_match.setdefault(match_id, {})[row.provider] = (
                row.external_id.removeprefix("match:")
            )
        for item in active + finished:
            if item.source and item.external_id:
                providers_by_match.setdefault(item.id, set()).add(item.source)
                provider_ids_by_match.setdefault(item.id, {})[item.source] = str(
                    item.external_id
                ).removeprefix("match:")

        stats_candidates = {
            item.id for item in finished
            if (
                (competition := competitions.get(item.competition_id))
                and competition_is_modeled(competition)
                and providers_by_match.get(item.id, set())
                & {"api_football", "sportmonks"}
            )
        }
        api_fixture_ids = {
            providers["api_football"]
            for match_id, providers in provider_ids_by_match.items()
            if match_id in stats_candidates and "api_football" in providers
        }
        attempt_rows = self.session.scalars(
            select(RawProviderPayloadRecord).where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == "statistics_attempt",
                RawProviderPayloadRecord.external_id.in_(
                    api_fixture_ids or {"-1"}
                ),
            ).order_by(RawProviderPayloadRecord.collected_at.desc())
        ).all()
        latest_attempt_by_fixture: dict[str, RawProviderPayloadRecord] = {}
        for row in attempt_rows:
            latest_attempt_by_fixture.setdefault(row.external_id, row)
        statistics_confirmed_unavailable = {
            match_id
            for match_id in stats_candidates - stats_ids
            if (
                "sportmonks" not in providers_by_match.get(match_id, set())
                and (
                    fixture_id := provider_ids_by_match.get(match_id, {}).get(
                        "api_football"
                    )
                ) is not None
                and (
                    attempt := latest_attempt_by_fixture.get(fixture_id)
                ) is not None
                and (attempt.payload or {}).get("status") == "empty"
            )
        }
        stats_eligible = stats_candidates - statistics_confirmed_unavailable
        odds_window_days = max(
            1, int(os.getenv("ODDS_SYNC_WINDOW_DAYS", "14"))
        )
        odds_window_end = naive + timedelta(days=odds_window_days)
        odds_eligible = {
            item.id for item in active
            if (
                naive - timedelta(hours=3)
                <= self._as_naive(item.kickoff_at)
                <= odds_window_end
                and
                (competition := competitions.get(item.competition_id))
                and competition_is_modeled(competition)
                and providers_by_match.get(item.id, set())
                & {"api_football", "football_data_uk", "the_odds_api"}
            )
        }
        provider_covered_odds = {
            int(value) for value in self.session.scalars(
                select(OddsSnapshotRecord.match_id).where(
                    OddsSnapshotRecord.match_id.in_(
                        [str(item) for item in odds_eligible] or ["-1"]
                    )
                ).distinct()
            ).all()
            if str(value).isdigit()
        }
        has_snapshot_contract = bool(provider_covered_odds)
        # Em bases mínimas/legadas sem snapshots, a odd atual ainda é evidência
        # de cobertura. No banco operacional, a série temporal é o contrato.
        if not provider_covered_odds:
            provider_covered_odds = odds_eligible & odds_ids
        latest_by_match = dict(self.session.execute(
            select(Odd.match_id, func.max(Odd.collected_at)).where(
                Odd.match_id.in_(provider_covered_odds or {-1})
            ).group_by(Odd.match_id)
        ).all())
        active_by_id = {item.id: item for item in active}
        odds_contract_fresh_ids: set[int] = set()
        for match_id in provider_covered_odds:
            match, latest = active_by_id.get(match_id), latest_by_match.get(match_id)
            if match is None or latest is None:
                continue
            until_kickoff = self._as_naive(match.kickoff_at) - naive
            maximum_age = (
                timedelta(minutes=10) if match.status == "in_progress"
                else timedelta(hours=2) if until_kickoff <= timedelta(hours=6)
                else timedelta(hours=8) if until_kickoff <= timedelta(hours=48)
                else timedelta(hours=48)
            )
            if latest >= naive - maximum_age:
                odds_contract_fresh_ids.add(match_id)
        if not has_snapshot_contract:
            odds_contract_fresh_ids = odds_ids & provider_covered_odds
        lineup_window = [
            item for item in active
            if naive - timedelta(minutes=30)
            <= self._as_naive(item.kickoff_at)
            <= naive + timedelta(minutes=120)
            and (
                (competition := competitions.get(item.competition_id))
                and competition_is_modeled(competition)
            )
            and providers_by_match.get(item.id, set())
            & {"api_football", "sportmonks"}
        ]
        lineup_ids = self._lineup_match_ids(lineup_window, now)

        raw = {
            "statistics": self._ratio(len(stats_ids), len(finished)),
            "odds": self._ratio(len(odds_ids), len(active)),
            "predictions": self._ratio(
                len(prediction_ids & prediction_eligible),
                len(prediction_eligible),
            ),
            "lineups": self._ratio(len(lineup_ids), len(active)),
        }
        coverage = {
            "statistics": self._ratio(
                len(stats_ids & stats_eligible), len(stats_eligible)
            ),
            "odds": self._ratio(
                len(odds_contract_fresh_ids), len(provider_covered_odds)
            ),
            "predictions": self._ratio(
                len(prediction_ids & prediction_eligible),
                len(prediction_eligible),
            ),
            "lineups": self._ratio(len(lineup_ids), len(lineup_window)),
        }
        competition_coverage: dict[str, dict[str, object]] = {}
        for competition_id, competition in competitions.items():
            policy = competition_policy(
                competition.name, competition.country
            )
            if policy is None and not competition.auto_core:
                continue
            metadata = competition_metadata(
                competition.name,
                competition.country,
                auto_core=competition.auto_core,
            )
            active_comp = {
                item.id for item in active
                if item.competition_id == competition_id
            }
            finished_comp = {
                item.id for item in finished
                if item.competition_id == competition_id
            }
            lineup_comp = {
                item.id for item in lineup_window
                if item.competition_id == competition_id
            }
            coverage_code = str(metadata["code"] or f"AUTO-{competition.id}")
            current = competition_coverage.setdefault(coverage_code, {
                "code": coverage_code,
                "name": str(metadata["canonical_name"]),
                "group": str(metadata["group"]),
                "promotion_source": (
                    "automatic" if competition.auto_core else "catalog"
                ),
                "active": 0,
                "finished": 0,
                "_active_ids": set(),
                "_finished_ids": set(),
                "_lineup_ids": set(),
            })
            current["_active_ids"].update(active_comp)
            current["_finished_ids"].update(finished_comp)
            current["_lineup_ids"].update(lineup_comp)
        for current in competition_coverage.values():
            comp_active = current.pop("_active_ids")
            comp_finished = current.pop("_finished_ids")
            comp_lineups = current.pop("_lineup_ids")
            current["active"] = len(comp_active)
            current["finished"] = len(comp_finished)
            current["statistics"] = self._ratio(
                len(stats_ids & comp_finished), len(comp_finished)
            )
            eligible_comp_odds = comp_active & odds_eligible
            current["odds"] = self._ratio(
                len(odds_ids & eligible_comp_odds), len(eligible_comp_odds)
            )
            current["predictions"] = self._ratio(
                len(prediction_ids & comp_active), len(comp_active)
            )
            current["lineups"] = self._ratio(
                len(lineup_ids & comp_lineups), len(comp_lineups)
            )

        latest_odds = self.session.scalar(select(func.max(Odd.collected_at)))
        closing_lines = int(self.session.scalar(
            select(func.count(func.distinct(Odd.match_id))).where(
                Odd.is_closing.is_(True),
                Odd.collected_at >= naive - timedelta(days=14),
            )
        ) or 0)
        odds_fresh = bool(
            latest_odds
            and latest_odds >= naive - timedelta(hours=6)
        )
        snapshot_filter = (
            OddsSnapshotRecord.match_id.in_([str(item) for item in provider_covered_odds] or ["-1"]),
            OddsSnapshotRecord.captured_at >= now - timedelta(days=14),
        )
        snapshot_count, odds_providers, odds_bookmakers, odds_markets = (
            self.session.execute(select(
                func.count(OddsSnapshotRecord.id),
                func.count(func.distinct(OddsSnapshotRecord.provider)),
                func.count(func.distinct(OddsSnapshotRecord.bookmaker)),
                func.count(func.distinct(OddsSnapshotRecord.market)),
            ).where(*snapshot_filter)).one()
        )
        capture_counts = self.session.execute(select(
            OddsSnapshotRecord.match_id,
            func.count(func.distinct(OddsSnapshotRecord.captured_at)),
        ).where(*snapshot_filter).group_by(OddsSnapshotRecord.match_id)).all()
        multi_snapshot_ids: set[int] = set()
        for match_id, capture_count in capture_counts:
            try:
                if int(capture_count) >= 2:
                    multi_snapshot_ids.add(int(match_id))
            except (TypeError, ValueError):
                continue
        in_progress = [item for item in active if item.status == "in_progress"]
        latest_live = self.session.scalar(
            select(func.max(LiveSnapshotRecord.captured_at))
        )
        live_freshness_minutes = max(
            2,
            (settings.live_sync_interval_seconds * 2 + 59) // 60,
        )
        live_fresh = not in_progress or bool(
            latest_live
            and self._as_aware(latest_live)
            >= now - timedelta(minutes=live_freshness_minutes)
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
        latest_statistics = self.session.scalar(
            select(func.max(RawProviderPayloadRecord.collected_at)).where(
                RawProviderPayloadRecord.resource.in_(
                    ("statistics", "statistics_attempt")
                )
            )
        )
        stats_fresh = bool(
            latest_statistics
            and self._as_aware(latest_statistics)
            >= now - timedelta(days=2)
        )
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
                "message": (
                    "Há partidas ao vivo sem snapshot dentro da janela "
                    f"operacional de {live_freshness_minutes} minutos."
                ),
            })
        recent_fusions = self.session.scalars(
            select(FusionResultRecord)
            .where(FusionResultRecord.canonical_id.like("match:%"))
            .order_by(FusionResultRecord.fused_at.desc())
            .limit(1000)
        ).all()
        effective_contributions: Counter[str] = Counter()
        candidate_contributions: Counter[str] = Counter()
        for fusion in recent_fusions:
            for detail in fusion.provenance.values():
                if not isinstance(detail, dict):
                    continue
                selected = detail.get("provider")
                if selected:
                    effective_contributions[str(selected)] += 1
                for provider in detail.get("contributors") or ():
                    candidate_contributions[str(provider)] += 1
        contribution_total = sum(effective_contributions.values())
        concentration = (
            max(effective_contributions.values()) / contribution_total
            if contribution_total else 0.0
        )
        report = {
            "quality_score": quality,
            "score_definition": "operational_sla",
            "window_days": 14,
            "matches": {
                "active": len(active), "finished": len(finished),
                "statistics_eligible": len(stats_eligible),
                "statistics_eligible_covered": len(stats_ids & stats_eligible),
                "statistics_eligible_missing": len(stats_eligible - stats_ids),
                "statistics_confirmed_unavailable": len(
                    statistics_confirmed_unavailable
                ),
                "statistics_available_recent": len(stats_ids),
                "odds_eligible": len(odds_eligible),
                "odds_provider_covered": len(provider_covered_odds),
                "odds_eligible_covered": len(odds_contract_fresh_ids),
                "predictions_eligible": len(prediction_eligible),
                "predictions_eligible_covered": len(prediction_ids & prediction_eligible),
                "lineups_eligible": len(lineup_window),
                "lineups_eligible_covered": len(lineup_ids),
            },
            "coverage": coverage,
            "raw_coverage": raw,
            "competition_coverage": sorted(
                competition_coverage.values(),
                key=lambda item: (
                    0 if item["group"] == "core" else 1,
                    item["name"],
                ),
            ),
            "freshness": {
                "latest_odds": latest_odds.isoformat() if latest_odds else None,
                "odds_stale": not odds_fresh,
                "latest_live": latest_live.isoformat() if latest_live else None,
                "live_stale": not live_fresh,
                "live_sla_minutes": live_freshness_minutes,
                "latest_statistics": (
                    latest_statistics.isoformat()
                    if latest_statistics else None
                ),
                "statistics_stale": not stats_fresh,
            },
            "odds_operations": {
                "snapshots_14d": int(snapshot_count),
                "providers_14d": int(odds_providers),
                "bookmakers_14d": int(odds_bookmakers),
                "markets_14d": int(odds_markets),
                "opening_lines": len(provider_covered_odds),
                "closing_lines_14d": closing_lines,
                "eligible_without_provider_coverage": len(odds_eligible - provider_covered_odds),
                "provider_covered_without_fresh_odds": len(provider_covered_odds - odds_contract_fresh_ids),
                "eligible_without_odds": len(odds_eligible - odds_ids),
                "matches_with_odds": len(odds_contract_fresh_ids),
                "matches_with_two_snapshots": len(multi_snapshot_ids & provider_covered_odds),
                "two_snapshot_coverage": self._ratio(
                    len(multi_snapshot_ids & provider_covered_odds), len(provider_covered_odds)
                ),
            },
            "data_contracts": self._g36_contracts(
                now=now, competitions=competition_coverage,
                coverage=coverage, raw=raw, odds_eligible=odds_eligible,
                odds_ids=odds_ids, provider_covered_odds=provider_covered_odds,
                odds_contract_fresh_ids=odds_contract_fresh_ids,
                stats_eligible=stats_eligible,
                stats_ids=stats_ids, lineup_window=lineup_window,
                lineup_ids=lineup_ids, multi_snapshot_ids=multi_snapshot_ids,
            ),
            "neutrality": {
                "base_weight": 1.0,
                "decision": "field_consensus_then_recency",
                "multi_provider_identity_coverage": multi_source,
                "effective_contributions": dict(effective_contributions),
                "candidate_contributions": dict(candidate_contributions),
                "largest_provider_share": round(concentration, 4),
                "capabilities": self.capabilities,
            },
            "providers": provider_status,
            "alerts": alerts,
        }
        if cache_enabled:
            self.__class__._cached_report = deepcopy(report)
            self.__class__._cached_at = now
        return report

    def _g36_contracts(self, *, now: datetime,
                       competitions: dict[str, dict[str, object]],
                       coverage: dict[str, float], raw: dict[str, float],
                       odds_eligible: set[int], odds_ids: set[int],
                       provider_covered_odds: set[int],
                       odds_contract_fresh_ids: set[int],
                       stats_eligible: set[int], stats_ids: set[int],
                       lineup_window: list[Match], lineup_ids: set[int],
                       multi_snapshot_ids: set[int]) -> dict[str, object]:
        freshness_sla = {
            "fixtures": 360, "results": 360, "odds": 360,
            "lineups": 120, "players": 1440, "events": 360,
            "statistics": 2880,
        }
        resource_aliases = {
            "fixtures": ("fixtures",), "results": ("fixtures", "live_details"),
            "odds": ("odds", "live_odds"), "lineups": ("lineups",),
            "players": ("player_statistics", "injuries"), "events": ("live_details",),
            "statistics": ("statistics", "statistics_attempt", "team_statistics"),
        }
        capabilities: dict[str, dict[str, object]] = {}
        for capability, resources in resource_aliases.items():
            latest = self.session.scalar(select(func.max(RawProviderPayloadRecord.collected_at)).where(
                RawProviderPayloadRecord.resource.in_(resources)
            ))
            age = ((now - self._as_aware(latest)).total_seconds() / 60) if latest else None
            capabilities[capability] = {
                "state": "unavailable" if latest is None else (
                    "available" if age <= freshness_sla[capability] else "stale"
                ),
                "latest_at": latest.isoformat() if latest else None,
                "age_minutes": round(age, 2) if age is not None else None,
                "sla_minutes": freshness_sla[capability],
            }
        identity_rows = self.session.scalars(
            select(IdentityDecisionRecord).order_by(
                IdentityDecisionRecord.decided_at.desc()
            ).limit(2000)
        ).all()
        identity_errors = sum(row.status in {"unmatched", "rejected"} for row in identity_rows)
        pending_quarantine = int(self.session.scalar(
            select(func.count()).select_from(DataQuarantineRecord).where(
                DataQuarantineRecord.resolved_at.is_(None)
            )
        ) or 0)
        missing_reasons = {
            "odds": {
                "provider_not_covering_or_not_returned": len(odds_eligible - provider_covered_odds),
                "covered_but_stale": len(provider_covered_odds - odds_contract_fresh_ids),
            },
            "statistics": {"eligible_not_returned": len(stats_eligible - stats_ids)},
            "lineups": {"not_published_in_match_window": len({m.id for m in lineup_window} - lineup_ids)},
        }
        quota = self.session.scalar(select(RawProviderPayloadRecord).where(
            RawProviderPayloadRecord.provider == "api_football",
            RawProviderPayloadRecord.resource == "quota",
        ).order_by(RawProviderPayloadRecord.collected_at.desc()))
        useful = len(odds_contract_fresh_ids) + len(stats_ids & stats_eligible) + len(lineup_ids)
        request_evidence = int(self.session.scalar(
            select(func.count()).select_from(RawProviderPayloadRecord).where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.collected_at >= now - timedelta(days=14),
                RawProviderPayloadRecord.resource.in_((
                    "odds", "statistics", "statistics_attempt", "lineups",
                    "player_statistics", "live_details",
                )),
            )
        ) or 0)
        gap_priorities = sorted((
            {"capability": "odds", "missing": len(provider_covered_odds - odds_contract_fresh_ids), "impact": 100,
             "reason": "necessária para EV, seleção e closing line"},
            {"capability": "statistics", "missing": len(stats_eligible - stats_ids), "impact": 90,
             "reason": "necessária para features e calibração"},
            {"capability": "lineups", "missing": len({m.id for m in lineup_window} - lineup_ids), "impact": 70,
             "reason": "ajuste contextual de jogadores"},
        ), key=lambda item: (-(item["impact"] if item["missing"] else 0), -item["missing"]))
        return {
            "definition_version": "g36-v1", "window_days": 14,
            "target_catalog": [
                {"code": item["code"], "name": item["name"], "group": item["group"],
                 "capabilities": tuple(resource_aliases)}
                for item in sorted(competitions.values(), key=lambda row: str(row["name"]))
            ],
            "denominators": {
                "statistics": {"raw_rate": raw["statistics"], "eligible_rate": coverage["statistics"],
                               "eligible": len(stats_eligible), "covered": len(stats_ids & stats_eligible)},
                "odds": {"raw_rate": raw["odds"], "eligible_rate": coverage["odds"],
                         "fixture_eligible": len(odds_eligible),
                         "provider_covered": len(provider_covered_odds),
                         "covered": len(odds_contract_fresh_ids)},
            },
            "freshness": capabilities,
            "odds_quality": {
                "fresh_eligible_coverage": coverage["odds"],
                "freshness_sla": {
                    "live_minutes": 10, "kickoff_under_6h_minutes": 120,
                    "kickoff_under_48h_minutes": 480, "distant_minutes": 2880,
                },
                "two_snapshot_coverage": self._ratio(len(multi_snapshot_ids & provider_covered_odds), len(provider_covered_odds)),
                "contract": "g36-odds-v1",
            },
            "identity": {
                "sampled": len(identity_rows), "errors": identity_errors,
                "sampled_error_rate": self._ratio(identity_errors, len(identity_rows)),
                "country_is_part_of_competition_identity": True,
            },
            "quarantine": {"pending": pending_quarantine, "reprocessing": "identity_pipeline"},
            "missing_reasons": missing_reasons,
            "gap_priorities": gap_priorities,
            "quota_efficiency": {
                "latest_provider_quota": quota.payload if quota else None,
                "useful_entities": useful,
                "request_evidence": request_evidence,
                "requests_per_useful_entity": round(request_evidence / useful, 4) if useful else None,
                "definition": "covered odds + statistics + lineups in active contract window",
            },
            "gates": {
                "statistics_eligible_90": coverage["statistics"] >= .90,
                "odds_fresh_80": coverage["odds"] >= .80,
                "two_snapshots_80": self._ratio(len(multi_snapshot_ids & provider_covered_odds), len(provider_covered_odds)) >= .80,
                "identity_error_below_0_5": self._ratio(identity_errors, len(identity_rows)) < .005,
                "missing_has_reason": True,
            },
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
            if match.source in {
                "api_football", "sportmonks"
            }:
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
        # O painel tolera dois ciclos da coleta completa antes de considerar
        # uma evidência expirada. Uma execução adiada não deve derrubar
        # visualmente provedores que continuam entregando dados.
        freshness_minutes = max(720, settings.sync_interval_minutes * 2)
        freshness_limit = now - timedelta(minutes=freshness_minutes)
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
            quota = (
                self.session.scalar(
                    select(RawProviderPayloadRecord)
                    .where(
                        RawProviderPayloadRecord.provider == provider,
                        RawProviderPayloadRecord.resource == "quota",
                    )
                    .order_by(
                        RawProviderPayloadRecord.collected_at.desc()
                    )
                )
                if provider == "api_football" else None
            )
            checked = bool(health or last_payload)
            health_recent = bool(
                health
                and health.available
                and self._as_aware(health.checked_at) >= freshness_limit
            )
            payload_recent = bool(
                last_payload
                and self._as_aware(last_payload) >= freshness_limit
            )
            result[provider] = {
                "checked": checked,
                "available": bool(checked and (health_recent or payload_recent)),
                "availability_evidence": (
                    "health_and_payload"
                    if health_recent and payload_recent
                    else "health"
                    if health_recent
                    else "payload"
                    if payload_recent
                    else "stale_or_failed"
                ),
                "freshness_sla_minutes": freshness_minutes,
                "latency_ms": health.latency_ms if health else None,
                "checked_at": health.checked_at.isoformat() if health else None,
                "last_payload_at": (
                    last_payload.isoformat() if last_payload else None
                ),
                "capabilities": self.capabilities.get(provider, ()),
                "base_weight": 1.0,
                "quota": quota.payload if quota else None,
            }
        return result

    @staticmethod
    def _ratio(numerator: int, denominator: int) -> float:
        # Ausência de amostra não é cobertura perfeita. Reportar zero evita
        # indicadores enganosos; a quantidade elegível permanece disponível
        # no relatório para distinguir "sem amostra" de "falha total".
        return round(numerator / denominator, 4) if denominator else 0.0

    @staticmethod
    def _as_aware(value: datetime) -> datetime:
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value

    @staticmethod
    def _as_naive(value: datetime) -> datetime:
        return (
            value.astimezone(timezone.utc).replace(tzinfo=None)
            if value.tzinfo is not None else value
        )
