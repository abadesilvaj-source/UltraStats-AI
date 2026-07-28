from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func, inspect, or_, select
from sqlalchemy.orm import Session, aliased

from app.models import (
    Audit,
    Bankroll,
    BetSlip,
    Competition,
    Market,
    Match,
    MatchStatistics,
    Odd,
    Prediction,
    Team,
)
from app.models.sync_run import SyncRun
from backend.serializers import iso_local
from app.services.maturity_service import MaturityService
from app.core.competition_catalog import competition_metadata
from ultrastats_ai.infrastructure.database.models import (
    FusionResultRecord,
    IdentityDecisionRecord,
    ModelValidationRecord,
    PredictiveModelRecord,
    ProviderHealthRecord,
    RawProviderPayloadRecord,
    RecommendationOpportunityRecord,
    TrainingDatasetRecord,
)


class ApiQueries:
    def __init__(self, session: Session, timezone_name: str) -> None:
        self.session = session
        self.timezone = timezone_name

    def matches(
        self,
        *,
        statuses: tuple[str, ...] = ("scheduled", "in_progress"),
        limit: int | None = 200,
        offset: int = 0,
    ) -> list[dict]:
        home, away = aliased(Team), aliased(Team)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        statement = (
            select(Match, home, away, Competition)
            .join(home, home.id == Match.home_team_id)
            .join(away, away.id == Match.away_team_id)
            .join(Competition, Competition.id == Match.competition_id)
            .order_by(Match.kickoff_at)
            .offset(offset)
        )
        conditions = []
        if {"scheduled", "not_started"} & set(statuses):
            conditions.append(and_(
                Match.status.in_(("scheduled", "not_started")),
                Match.kickoff_at >= now - timedelta(minutes=45),
            ))
        if "in_progress" in statuses:
            conditions.append(and_(
                Match.status == "in_progress",
                Match.kickoff_at >= now - timedelta(days=30),
            ))
        if "finished" in statuses:
            conditions.append(and_(
                Match.status == "finished",
                Match.kickoff_at >= now - timedelta(days=30),
            ))
        terminal = set(statuses) & {"postponed", "cancelled"}
        if terminal:
            conditions.append(Match.status.in_(terminal))
        if conditions:
            statement = statement.where(or_(*conditions))
        else:
            statement = statement.where(
                Match.status.in_(statuses)
            )
        if limit is not None:
            statement = statement.limit(limit)
        rows = self.session.execute(statement).all()
        return [
            {
                "id": match.id,
                "external_id": match.external_id,
                "status": (
                    "finished"
                    if match.status == "in_progress"
                    and match.kickoff_at < now - timedelta(hours=4)
                    else match.status
                ),
                "kickoff_at": iso_local(match.kickoff_at, self.timezone),
                "timezone": self.timezone,
                "competition": {
                    "id": competition.id,
                    "name": competition.name,
                    "country": competition.country,
                    **competition_metadata(
                        competition.name, competition.country
                    ),
                },
                "home_team": {"id": h.id, "name": h.name},
                "away_team": {"id": a.id, "name": a.name},
                "score": {"home": match.home_score, "away": match.away_score},
                "venue": match.venue,
                "source": match.source,
            }
            for match, h, a, competition in rows
        ]

    def match_detail(self, match_id: int) -> dict:
        base = next(
            (item for item in self.matches(statuses=(
                "scheduled", "not_started", "in_progress", "finished",
                "postponed", "cancelled",
            ), limit=None) if item["id"] == match_id),
            None,
        )
        if base is None:
            raise ValueError("Partida não encontrada.")
        statistics = self.session.scalar(
            select(MatchStatistics).where(MatchStatistics.match_id == match_id)
        )
        base["statistics"] = (
            {
                column: getattr(statistics, column)
                for column in (
                    "corners_home", "corners_away", "yellow_cards_home",
                    "yellow_cards_away", "red_cards_home", "red_cards_away",
                    "shots_home", "shots_away", "shots_on_target_home",
                    "shots_on_target_away", "offsides_home", "offsides_away",
                    "possession_home", "possession_away", "xg_home", "xg_away",
                )
            }
            if statistics else None
        )
        base["markets"] = self.match_markets(match_id)
        base["analysis"] = self.predictions(match_id=match_id)
        base["recommendations"] = self.recommendations(match_id=match_id)
        base["lineups"] = self.lineups(match_id)
        fusion = self.session.scalar(
            select(FusionResultRecord)
            .where(FusionResultRecord.canonical_id == f"match:{match_id}")
            .order_by(FusionResultRecord.fused_at.desc())
        )
        base["data_fusion"] = (
            {
                "values": fusion.values,
                "provenance": fusion.provenance,
                "conflicts": fusion.conflicts,
                "fused_at": fusion.fused_at.isoformat(),
            }
            if fusion else None
        )
        return base

    def lineups(self, match_id: int) -> list[dict]:
        match = self.session.get(Match, match_id)
        if match is None:
            return []
        identities = {
            item.provider: item.external_id.removeprefix("match:")
            for item in self.session.scalars(
                select(IdentityDecisionRecord).where(
                    IdentityDecisionRecord.candidate_id
                    == f"match:{match_id}",
                    IdentityDecisionRecord.status == "matched",
                )
            ).all()
        }
        if match.source and match.external_id:
            identities.setdefault(match.source, str(match.external_id))
        api_id = identities.get("api_football")
        rows = self.session.scalars(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == "lineups",
                RawProviderPayloadRecord.external_id.like(
                    f"{api_id}:%"
                ) if api_id else False,
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
        ).all()
        result, seen = [], set()
        for row in rows:
            team = row.payload.get("team", {})
            team_id = str(team.get("id") or "")
            if not team_id or team_id in seen:
                continue
            seen.add(team_id)
            result.append(
                {
                    "team": team,
                    "formation": row.payload.get("formation"),
                    "coach": row.payload.get("coach"),
                    "start_xi": [
                        item.get("player", {})
                        for item in row.payload.get("startXI", [])
                    ],
                    "substitutes": [
                        item.get("player", {})
                        for item in row.payload.get("substitutes", [])
                    ],
                    "confirmed": len(row.payload.get("startXI", [])) >= 11,
                    "collected_at": row.collected_at.isoformat(),
                    "provider": "api_football",
                }
            )
        sportmonks_id = identities.get("sportmonks")
        sportmonks = self.session.scalar(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider == "sportmonks",
                RawProviderPayloadRecord.resource == "lineups",
                RawProviderPayloadRecord.external_id == sportmonks_id,
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
        ) if sportmonks_id else None
        if sportmonks:
            result.extend(
                self._sportmonks_lineups(sportmonks.payload)
            )
        return result

    @staticmethod
    def _sportmonks_lineups(payload: dict) -> list[dict]:
        participants = {
            str(item.get("id")): item
            for item in payload.get("participants", ())
            if isinstance(item, dict)
        }
        grouped: dict[str, list[dict]] = {}
        for item in payload.get("lineups", ()):
            if not isinstance(item, dict):
                continue
            team_id = str(
                item.get("participant_id")
                or item.get("team_id")
                or ""
            )
            grouped.setdefault(team_id, []).append(item)
        result = []
        for team_id, entries in grouped.items():
            starters, substitutes = [], []
            for entry in entries:
                player = entry.get("player") or {}
                normalized = {
                    "id": player.get("id"),
                    "name": player.get("display_name")
                    or player.get("name"),
                    "number": entry.get("jersey_number"),
                    "pos": entry.get("position")
                    or entry.get("formation_position"),
                }
                target = (
                    starters
                    if entry.get("starter")
                    or entry.get("type_id") in {11, 12}
                    else substitutes
                )
                target.append(normalized)
            result.append({
                "team": participants.get(team_id, {"id": team_id}),
                "formation": None,
                "coach": None,
                "start_xi": starters,
                "substitutes": substitutes,
                "confirmed": len(starters) >= 11,
                "provider": "sportmonks",
            })
        return result

    def match_markets(self, match_id: int) -> list[dict]:
        rows = self.session.execute(
            select(Odd, Market)
            .join(Market, Market.id == Odd.market_id)
            .where(Odd.match_id == match_id, Market.active.is_(True))
            .order_by(Market.category, Market.name, Odd.collected_at.desc())
        ).all()
        seen = set()
        grouped: dict[int, dict] = {}
        for odd, market in rows:
            key = (market.id, odd.selection, odd.bookmaker)
            if key in seen:
                continue
            seen.add(key)
            target = grouped.setdefault(
                market.id,
                {
                    "id": market.id,
                    "code": market.code,
                    "name": market.name,
                    "category": market.category,
                    "options": [],
                },
            )
            target["options"].append(
                {
                    "selection": odd.selection,
                    "odd": float(odd.odd_value),
                    "bookmaker": odd.bookmaker,
                    "collected_at": odd.collected_at.isoformat(),
                }
            )
        prediction_rows = self.session.execute(
            select(Prediction, Market)
            .join(Market, Market.id == Prediction.market_id)
            .where(
                Prediction.match_id == match_id,
                Market.active.is_(True),
            )
            .order_by(Prediction.created_at.desc())
        ).all()
        existing_options = {
            (market_id, option["selection"].casefold())
            for market_id, item in grouped.items()
            for option in item["options"]
        }
        for prediction, market in prediction_rows:
            key = (market.id, prediction.selection.casefold())
            if key in existing_options:
                continue
            existing_options.add(key)
            target = grouped.setdefault(
                market.id,
                {
                    "id": market.id,
                    "code": market.code,
                    "name": market.name,
                    "category": market.category,
                    "options": [],
                },
            )
            target["options"].append({
                "selection": prediction.selection,
                "odd": round(
                    1 / max(float(prediction.probability), .001), 2
                ),
                "bookmaker": "Odd justa do modelo",
                "collected_at": prediction.created_at.isoformat(),
            })
        return list(grouped.values())

    def predictions(
        self, match_id: int | None = None, limit: int | None = None
    ) -> list[dict]:
        home, away = aliased(Team), aliased(Team)
        statement = (
            select(Prediction, Match, Market, home, away, Competition)
            .join(Match, Match.id == Prediction.match_id)
            .join(Market, Market.id == Prediction.market_id)
            .join(home, home.id == Match.home_team_id)
            .join(away, away.id == Match.away_team_id)
            .join(Competition, Competition.id == Match.competition_id)
            .where(Match.status.in_(("scheduled", "in_progress")))
            .where(
                Match.kickoff_at
                >= datetime.now(timezone.utc).replace(tzinfo=None)
                - timedelta(hours=2)
            )
            .order_by(Match.kickoff_at, Prediction.expected_value.desc())
        )
        if match_id is not None:
            statement = statement.where(Match.id == match_id)
        if limit is not None:
            statement = statement.limit(limit)
        return [
            {
                "id": p.id,
                "match_id": match.id,
                "match": f"{home_team.name} x {away_team.name}",
                "competition": competition.name,
                "kickoff_at": iso_local(match.kickoff_at, self.timezone),
                "market_id": market.id,
                "market": market.name,
                "market_category": market.category,
                "selection": p.selection,
                "probability": p.probability,
                "implied_probability": p.implied_probability,
                "expected_value": p.expected_value,
                "confidence": p.confidence,
                "evidence": p.evidence_level,
                "risk": p.risk_level,
                "model": p.model_version,
            }
            for p, match, market, home_team, away_team, competition
            in self.session.execute(statement).all()
        ]

    def recommendations(
        self,
        match_id: int | None = None,
        primary_only: bool = False,
        limit: int | None = None,
    ) -> list[dict]:
        has_opportunities = inspect(
            self.session.connection()
        ).has_table(
            RecommendationOpportunityRecord.__tablename__
        )
        latest_evaluation = (
            self.session.scalar(
                select(
                    func.max(
                        RecommendationOpportunityRecord.evaluated_at
                    )
                )
            )
            if has_opportunities else None
        )
        opportunities = (
            self.session.scalars(
                select(RecommendationOpportunityRecord).where(
                    RecommendationOpportunityRecord.evaluated_at
                    == latest_evaluation
                )
            ).all()
            if latest_evaluation else []
        )
        opportunity_map = {
            (
                int(item.match_id),
                item.market,
                item.selection,
            ): item
            for item in opportunities
        }
        market_codes = {
            item.id: item.code
            for item in self.session.scalars(select(Market)).all()
        }
        prediction_rows = self.predictions(match_id=match_id)
        grouped: dict[tuple[int, int], list[dict]] = {}
        best: dict[tuple[int, int], dict] = {}
        for row in prediction_rows:
            key = (row["match_id"], row["market_id"])
            grouped.setdefault(key, []).append(row)
            current = best.get(key)
            if current is None or row["probability"] > current["probability"]:
                best[key] = row
        result = []
        for row in best.values():
            opportunity = opportunity_map.get(
                (
                    row["match_id"],
                    market_codes[row["market_id"]],
                    row["selection"],
                )
            )
            actionable = bool(
                opportunity.safe if opportunity else (
                    row["expected_value"] is not None
                    and row["expected_value"] > 0
                    and row["evidence"] != "low"
                )
            )
            ordered = sorted(
                grouped[(row["match_id"], row["market_id"])],
                key=lambda item: item["probability"],
                reverse=True,
            )
            probability_margin = (
                ordered[0]["probability"] - ordered[1]["probability"]
                if len(ordered) > 1 else ordered[0]["probability"]
            )
            no_bet = bool(
                not actionable
                and (
                    row["expected_value"] is None
                    or probability_margin < .08
                    or row["evidence"] == "low"
                )
            )
            result.append({
                **row,
                "display_selection": row["selection"],
                "no_bet": no_bet,
                "is_primary_recommendation": actionable,
                "probability_margin": probability_margin,
                "actionable": actionable,
                "recommendation_type": (
                    "value_bet" if actionable else "model_lead"
                ),
                "blocked_reasons": (
                    opportunity.blocked_reasons
                    if opportunity else []
                ),
                "warnings": (
                    opportunity.metrics.get("warnings", [])
                    if opportunity else []
                ),
                "recommendation_score": (
                    float(opportunity.score)
                    if opportunity else None
                ),
                "probability_interval": (
                    opportunity.metrics.get("probability_interval")
                    if opportunity else None
                ),
                "conservative_expected_value": (
                    opportunity.metrics.get(
                        "conservative_expected_value"
                    )
                    if opportunity else None
                ),
                "fractional_kelly": (
                    opportunity.metrics.get("fractional_kelly")
                    if opportunity else None
                ),
                "odds_age_hours": (
                    opportunity.metrics.get("odds_age_hours")
                    if opportunity else None
                ),
                "market_samples": (
                    opportunity.metrics.get("market_samples")
                    if opportunity else None
                ),
            })
        correlated_codes = {
            "over_2_5_goals", "under_2_5_goals", "under_3_5_goals",
            "both_teams_to_score",
        }
        by_match: dict[int, list[dict]] = {}
        for item in result:
            if (
                item["actionable"]
                and market_codes[item["market_id"]] in correlated_codes
            ):
                by_match.setdefault(item["match_id"], []).append(item)
        for items in by_match.values():
            keep = max(
                items,
                key=lambda item: (
                    item["conservative_expected_value"] or -1,
                    item["recommendation_score"] or -1,
                ),
            )
            for item in items:
                if item is keep:
                    continue
                item["actionable"] = False
                item["no_bet"] = True
                item["is_primary_recommendation"] = False
                item["recommendation_type"] = "model_lead"
                item["blocked_reasons"] = [
                    *item["blocked_reasons"],
                    "correlated_market_exposure",
                ]
        all_by_match: dict[int, list[dict]] = {}
        for item in result:
            all_by_match.setdefault(item["match_id"], []).append(item)
        evidence_weight = {"high": 3, "medium": 2, "low": 1}
        for items in all_by_match.values():
            if any(item["actionable"] for item in items):
                continue
            primary = max(
                items,
                key=lambda item: (
                    item["recommendation_score"] or -1,
                    evidence_weight.get(item["evidence"], 0),
                    item["confidence"] or 0,
                    item["probability_margin"],
                    item["probability"],
                ),
            )
            primary["no_bet"] = False
            primary["is_primary_recommendation"] = True
            primary["recommendation_type"] = "model_pick"
            primary["warnings"] = [
                *primary["warnings"],
                "model_pick_without_confirmed_value",
            ]
        if primary_only:
            result = [
                item for item in result
                if item["is_primary_recommendation"]
            ]
        return result[:limit] if limit is not None else result

    def markets(self) -> list[dict]:
        return [
            {
                "id": market.id,
                "code": market.code,
                "name": market.name,
                "category": market.category,
                "active": market.active,
            }
            for market in self.session.scalars(
                select(Market).order_by(Market.category, Market.name)
            )
        ]

    def bankrolls(self) -> list[dict]:
        return [
            {
                "id": item.id,
                "name": item.name,
                "currency": item.currency,
                "balance": float(item.current_balance),
                "initial_balance": float(item.initial_balance),
                "unit_percentage": item.unit_percentage,
                "active": item.active,
            }
            for item in self.session.scalars(select(Bankroll).order_by(Bankroll.id))
        ]

    def system_status(self) -> dict:
        latest = self.session.scalar(
            select(SyncRun).order_by(SyncRun.started_at.desc())
        )
        health_rows = self.session.scalars(
            select(ProviderHealthRecord).order_by(
                ProviderHealthRecord.checked_at.desc()
            )
        ).all()
        providers, seen = [], set()
        capability_map = {
            "api_football": [
                "fixtures", "live", "statistics", "odds", "events", "lineups"
            ],
            "football_data": ["competitions", "fixtures", "scores"],
            "football_data_uk": ["historical_results", "historical_odds"],
            "openligadb": ["fixtures", "scores"],
            "statsbomb_open_data": ["historical_events", "xg"],
            "thesportsdb": [
                "fixtures", "scores", "teams", "venues", "metadata"
            ],
            "sportmonks": [
                "fixtures", "scores", "statistics", "events", "lineups",
                "injuries", "xg",
            ],
            "the_odds_api": ["odds", "scores"],
            "goal_api": ["fixtures", "live", "scores", "venues"],
            "zafronix": [
                "fixtures", "live", "scores", "statistics", "events",
                "lineups", "weather",
            ],
        }
        for row in health_rows:
            if row.provider in seen:
                continue
            seen.add(row.provider)
            providers.append({
                "name": row.provider,
                "available": row.available,
                "message": row.message,
                "latency_ms": row.latency_ms,
                "checked_at": row.checked_at.isoformat(),
                "capabilities": capability_map.get(row.provider, []),
            })
        return {
            "status": "healthy",
            "server_time": datetime.now(timezone.utc).isoformat(),
            "timezone": self.timezone,
            "counts": {
                "matches": self.session.scalar(
                    select(func.count()).select_from(Match)
                ),
                "predictions": self.session.scalar(
                    select(func.count()).select_from(Prediction)
                ),
                "markets": self.session.scalar(
                    select(func.count()).select_from(Market)
                ),
                "bet_slips": self.session.scalar(
                    select(func.count()).select_from(BetSlip)
                ),
            },
            "last_sync": (
                {
                    "id": latest.id,
                    "status": latest.status,
                    "source": latest.source,
                    "started_at": latest.started_at.isoformat(),
                    "finished_at": (
                        latest.finished_at.isoformat() if latest.finished_at else None
                    ),
                }
                if latest else None
            ),
            "providers": providers,
            "data_fusion": self.fusion_contributions(),
            "intelligence": self.intelligence_status(),
        }

    def maturity_status(self) -> dict:
        return MaturityService(self.session).report()

    def intelligence_status(self) -> dict:
        latest_validation = self.session.scalar(
            select(ModelValidationRecord)
            .order_by(ModelValidationRecord.evaluated_at.desc())
        )
        statistics_updated_at = self.session.scalar(
            select(func.max(MatchStatistics.updated_at))
        )
        latest_recommendation_evaluation = self.session.scalar(
            select(
                func.max(RecommendationOpportunityRecord.evaluated_at)
            )
        )
        current_recommendations = (
            RecommendationOpportunityRecord.evaluated_at
            == latest_recommendation_evaluation
        )
        return {
            "statistics": {
                "matches_with_statistics": self.session.scalar(
                    select(func.count()).select_from(MatchStatistics)
                ) or 0,
                "last_update": (
                    statistics_updated_at.isoformat()
                    if statistics_updated_at
                    else None
                ),
                "recent_attempts": self.session.scalar(
                    select(func.count())
                    .select_from(RawProviderPayloadRecord)
                    .where(
                        RawProviderPayloadRecord.resource
                        == "statistics_attempt",
                        RawProviderPayloadRecord.collected_at
                        >= datetime.now(timezone.utc)
                        - timedelta(hours=24),
                    )
                ) or 0,
            },
            "learning": {
                "audited_predictions": self.session.scalar(
                    select(func.count()).select_from(Audit)
                ) if inspect(self.session.connection()).has_table(
                    Audit.__tablename__
                ) else 0,
                "registered_models": self.session.scalar(
                    select(func.count()).select_from(PredictiveModelRecord)
                ) or 0,
                "training_datasets": self.session.scalar(
                    select(func.count()).select_from(TrainingDatasetRecord)
                ) or 0,
                "latest_validation": (
                    {
                        "approved": latest_validation.approved,
                        "metrics": latest_validation.metrics,
                        "gate_failures":
                            latest_validation.gate_failures,
                        "evaluated_at":
                            latest_validation.evaluated_at.isoformat(),
                    }
                    if latest_validation else None
                ),
            },
            "recommendations": {
                "persisted": self.session.scalar(
                    select(func.count())
                    .select_from(RecommendationOpportunityRecord)
                    .where(
                        current_recommendations
                    )
                ) or 0,
                "safe": self.session.scalar(
                    select(func.count())
                    .select_from(RecommendationOpportunityRecord)
                    .where(
                        current_recommendations,
                        RecommendationOpportunityRecord.safe.is_(True),
                    )
                ) or 0,
            },
        }

    def fusion_contributions(self) -> dict:
        rows = self.session.scalars(
            select(FusionResultRecord)
            .where(FusionResultRecord.canonical_id.like("match:%"))
            .order_by(FusionResultRecord.fused_at.desc())
            .limit(1000)
        ).all()
        provider_fields: Counter[str] = Counter()
        provider_candidates: Counter[str] = Counter()
        conflicts = 0
        for row in rows:
            conflicts += len(row.conflicts)
            for detail in row.provenance.values():
                if isinstance(detail, dict) and detail.get("provider"):
                    provider_fields[str(detail["provider"])] += 1
                    for provider in detail.get("contributors", ()):
                        provider_candidates[str(provider)] += 1
        identities_by_provider = dict(
            self.session.execute(
                select(
                    IdentityDecisionRecord.provider,
                    func.count(IdentityDecisionRecord.id),
                )
                .where(
                    IdentityDecisionRecord.external_id.like("match:%"),
                    IdentityDecisionRecord.status == "matched",
                )
                .group_by(IdentityDecisionRecord.provider)
            ).all()
        )
        training = self.session.scalar(
            select(FusionResultRecord)
            .where(FusionResultRecord.canonical_id.like("training:%"))
            .order_by(FusionResultRecord.fused_at.desc())
            .limit(1)
        )
        return {
            "recent_fusions": len(rows),
            "matched_identities": sum(identities_by_provider.values()),
            "matched_identities_by_provider": identities_by_provider,
            "conflicts_detected": conflicts,
            "fields_selected_by_provider": dict(provider_fields),
            "field_candidates_by_provider": dict(provider_candidates),
            "latest_historical_enrichment": (
                {
                    "source": next(
                        (
                            detail.get("provider")
                            for detail in training.provenance.values()
                            if isinstance(detail, dict)
                            and detail.get("provider")
                        ),
                        None,
                    ),
                    **training.values,
                    "applied_at": training.fused_at.isoformat(),
                }
                if training else None
            ),
        }
