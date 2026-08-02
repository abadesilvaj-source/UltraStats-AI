from collections import Counter
from datetime import datetime, timedelta, timezone
import os

from sqlalchemy import Float, and_, cast, func, inspect, or_, select
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
from api.serializers import iso_local
from app.services.maturity_service import MaturityService
from app.services.intelligence_platform_service import (
    IntelligencePlatformService,
)
from app.core.competition_catalog import competition_metadata
from ultrastats_ai.infrastructure.database.models import (
    FusionResultRecord,
    IdentityDecisionRecord,
    ModelValidationRecord,
    PredictiveModelRecord,
    ProviderHealthRecord,
    PredictionExplanationRecord,
    RawProviderPayloadRecord,
    RecommendationOpportunityRecord,
    PaperBetRecord,
    PaperLearningRunRecord,
    PaperPortfolioRecord,
    TrainingDatasetRecord,
)


# Uma partida de futebol pode ultrapassar duas horas por acréscimos,
# intervalo e prorrogação. Depois de três horas, porém, manter um evento
# como ao vivo quase sempre representa um estado terminal atrasado no feed.
MAX_LIVE_MATCH_AGE = timedelta(hours=3)


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
                Match.kickoff_at >= now - timedelta(hours=12),
            ))
        if "finished" in statuses:
            conditions.append(and_(
                Match.kickoff_at >= now - timedelta(days=30),
                or_(
                    Match.status == "finished",
                    and_(
                        Match.status == "in_progress",
                        Match.kickoff_at < now - MAX_LIVE_MATCH_AGE,
                    ),
                ),
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
                    and match.kickoff_at < now - MAX_LIVE_MATCH_AGE
                    else match.status
                ),
                "kickoff_at": iso_local(match.kickoff_at, self.timezone),
                "timezone": self.timezone,
                "competition": {
                    "id": competition.id,
                    "name": competition.name,
                    "country": competition.country,
                    **competition_metadata(
                        competition.name, competition.country,
                        auto_core=competition.auto_core,
                    ),
                    "promotion_status": competition.promotion_status,
                    "promotion_metrics": competition.promotion_metrics,
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
                    "shots_off_target_home", "shots_off_target_away",
                    "blocked_shots_home", "blocked_shots_away",
                    "shots_inside_box_home", "shots_inside_box_away",
                    "shots_outside_box_home", "shots_outside_box_away",
                    "fouls_home", "fouls_away",
                    "goalkeeper_saves_home", "goalkeeper_saves_away",
                    "passes_home", "passes_away",
                    "passes_accurate_home", "passes_accurate_away",
                    "pass_accuracy_home", "pass_accuracy_away",
                )
            }
            if statistics else None
        )
        base["markets"] = self.match_markets(match_id)
        base["analysis"] = self.predictions(match_id=match_id)
        base["recommendations"] = self.recommendations(match_id=match_id)
        base["lineups"] = self.lineups(match_id)
        base["events"] = self.events(match_id)
        base["analysis_context"] = self.analysis_context(match_id)
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

    def analysis_context(self, match_id: int) -> dict:
        """Build a factual, pre-match context from previously finished games."""
        target = self.session.get(Match, match_id)
        if target is None:
            return {}

        home_alias, away_alias = aliased(Team), aliased(Team)

        def recent(team_id: int, limit: int = 5) -> list[dict]:
            statement = (
                select(
                    Match, home_alias, away_alias, Competition,
                    MatchStatistics,
                )
                .join(home_alias, home_alias.id == Match.home_team_id)
                .join(away_alias, away_alias.id == Match.away_team_id)
                .join(Competition, Competition.id == Match.competition_id)
                .outerjoin(
                    MatchStatistics,
                    MatchStatistics.match_id == Match.id,
                )
                .where(
                    Match.id != match_id,
                    Match.status == "finished",
                    Match.kickoff_at < target.kickoff_at,
                    or_(
                        Match.home_team_id == team_id,
                        Match.away_team_id == team_id,
                    ),
                    Match.home_score.is_not(None),
                    Match.away_score.is_not(None),
                )
                .order_by(Match.kickoff_at.desc())
                .limit(limit)
            )
            result = []
            for game, home, away, competition, stats in self.session.execute(statement):
                is_home = game.home_team_id == team_id
                goals_for = game.home_score if is_home else game.away_score
                goals_against = game.away_score if is_home else game.home_score
                result.append({
                    "id": game.id,
                    "kickoff_at": iso_local(game.kickoff_at, self.timezone),
                    "competition": competition.name,
                    "home_team": home.name,
                    "away_team": away.name,
                    "home_score": game.home_score,
                    "away_score": game.away_score,
                    "result": (
                        "V" if goals_for > goals_against
                        else "E" if goals_for == goals_against else "D"
                    ),
                    "goals_for": goals_for,
                    "goals_against": goals_against,
                    "statistics_available": stats is not None,
                    "corners": (
                        (stats.corners_home if is_home else stats.corners_away)
                        if stats else None
                    ),
                    "cards": (
                        (
                            (stats.yellow_cards_home or 0)
                            + (stats.red_cards_home or 0)
                        ) if stats and is_home else (
                            (stats.yellow_cards_away or 0)
                            + (stats.red_cards_away or 0)
                        ) if stats else None
                    ),
                })
            return result

        home_recent = recent(target.home_team_id)
        away_recent = recent(target.away_team_id)

        h2h_statement = (
            select(Match, home_alias, away_alias, Competition)
            .join(home_alias, home_alias.id == Match.home_team_id)
            .join(away_alias, away_alias.id == Match.away_team_id)
            .join(Competition, Competition.id == Match.competition_id)
            .where(
                Match.id != match_id,
                Match.status == "finished",
                Match.kickoff_at < target.kickoff_at,
                or_(
                    and_(
                        Match.home_team_id == target.home_team_id,
                        Match.away_team_id == target.away_team_id,
                    ),
                    and_(
                        Match.home_team_id == target.away_team_id,
                        Match.away_team_id == target.home_team_id,
                    ),
                ),
                Match.home_score.is_not(None),
                Match.away_score.is_not(None),
            )
            .order_by(Match.kickoff_at.desc())
            .limit(5)
        )
        h2h = [{
            "id": game.id,
            "kickoff_at": iso_local(game.kickoff_at, self.timezone),
            "competition": competition.name,
            "home_team": home.name,
            "away_team": away.name,
            "home_score": game.home_score,
            "away_score": game.away_score,
        } for game, home, away, competition in self.session.execute(h2h_statement)]

        home_team = self.session.get(Team, target.home_team_id)
        away_team = self.session.get(Team, target.away_team_id)

        def metrics(games: list[dict]) -> dict:
            count = len(games)
            if not count:
                return {"sample": 0}
            wins = sum(game["result"] == "V" for game in games)
            draws = sum(game["result"] == "E" for game in games)
            losses = count - wins - draws
            goals_for = sum(game["goals_for"] for game in games)
            goals_against = sum(game["goals_against"] for game in games)
            statistical = [game for game in games if game["statistics_available"]]
            return {
                "sample": count,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "win_rate": wins / count,
                "unbeaten_rate": (wins + draws) / count,
                "goals_for_average": goals_for / count,
                "goals_against_average": goals_against / count,
                "over_2_5_rate": sum(
                    game["goals_for"] + game["goals_against"] > 2
                    for game in games
                ) / count,
                "btts_rate": sum(
                    game["goals_for"] > 0 and game["goals_against"] > 0
                    for game in games
                ) / count,
                "statistics_sample": len(statistical),
                "corners_average": (
                    sum(game["corners"] for game in statistical) / len(statistical)
                    if statistical and all(game["corners"] is not None for game in statistical)
                    else None
                ),
                "cards_average": (
                    sum(game["cards"] for game in statistical) / len(statistical)
                    if statistical and all(game["cards"] is not None for game in statistical)
                    else None
                ),
            }

        home_metrics, away_metrics = metrics(home_recent), metrics(away_recent)
        home_name = home_team.name if home_team else "Mandante"
        away_name = away_team.name if away_team else "Visitante"
        factors = []
        for name, values in ((home_name, home_metrics), (away_name, away_metrics)):
            sample = values.get("sample", 0)
            if not sample:
                continue
            factors.append(
                f"{name}: {values['wins']}V, {values['draws']}E e "
                f"{values['losses']}D nos últimos {sample} jogos; média de "
                f"{values['goals_for_average']:.1f} gol(s) marcado(s)."
            )
            if values["over_2_5_rate"] >= .6:
                factors.append(
                    f"{name}: mais de 2,5 gols ocorreu em "
                    f"{values['over_2_5_rate'] * 100:.0f}% dessa amostra."
                )
            if values.get("corners_average") is not None:
                factors.append(
                    f"{name}: média de {values['corners_average']:.1f} "
                    f"escanteio(s) em {values['statistics_sample']} jogo(s) com dados completos."
                )
        if h2h:
            factors.append(
                f"Há {len(h2h)} confronto(s) direto(s) anterior(es) disponível(is) para comparação."
            )

        if home_recent and away_recent:
            summary = (
                f"{home_name} recebe {away_name}. Nos últimos "
                f"{len(home_recent)} jogos, o mandante somou "
                f"{home_metrics['wins']} vitória(s) e marcou em média "
                f"{home_metrics['goals_for_average']:.1f} gol(s); o visitante, "
                f"em {len(away_recent)} jogos, obteve {away_metrics['wins']} vitória(s) "
                f"e média de {away_metrics['goals_for_average']:.1f} gol(s). "
                "A análise considera somente partidas anteriores a este confronto."
            )
        else:
            summary = (
                f"{home_name} enfrenta {away_name}. Ainda não há histórico encerrado "
                "suficiente na base para produzir um resumo estatístico confiável."
            )

        return {
            "summary": summary,
            "home_recent": home_recent,
            "away_recent": away_recent,
            "home_metrics": home_metrics,
            "away_metrics": away_metrics,
            "key_factors": factors[:6],
            "h2h": h2h,
        }

    def events(self, match_id: int) -> list[dict]:
        match = self.session.get(Match, match_id)
        if match is None:
            return []
        api_id = None
        decision = self.session.scalar(
            select(IdentityDecisionRecord).where(
                IdentityDecisionRecord.provider == "api_football",
                IdentityDecisionRecord.candidate_id == f"match:{match_id}",
                IdentityDecisionRecord.status == "matched",
            )
        )
        if decision:
            api_id = decision.external_id.removeprefix("match:")
        if api_id is None and str(match.external_id).startswith(
            "api_football:"
        ):
            api_id = str(match.external_id).split(":", 1)[1]
        if not api_id:
            return []
        home_team = self.session.get(Team, match.home_team_id)
        away_team = self.session.get(Team, match.away_team_id)
        rows = self.session.scalars(
            select(RawProviderPayloadRecord).where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == "events",
                RawProviderPayloadRecord.external_id.like(f"{api_id}:%"),
            ).order_by(RawProviderPayloadRecord.collected_at.desc())
        ).all()
        result, seen = [], set()
        for row in rows:
            payload = row.payload
            event_id = str(
                payload.get("id")
                or row.external_id.rsplit(":", 1)[-1]
            )
            signature = (
                str((payload.get("time") or {}).get("elapsed")),
                str((payload.get("time") or {}).get("extra")),
                str(payload.get("type")),
                str(payload.get("detail")),
                str((payload.get("team") or {}).get("id")),
            )
            if signature in seen:
                continue
            seen.add(signature)
            team_id = (payload.get("team") or {}).get("id")
            team_name = str(
                (payload.get("team") or {}).get("name") or ""
            ).casefold()
            result.append({
                "id": event_id,
                "minute": (payload.get("time") or {}).get("elapsed"),
                "extra": (payload.get("time") or {}).get("extra"),
                "type": payload.get("type"),
                "detail": payload.get("detail"),
                "comments": payload.get("comments"),
                "player": payload.get("player") or {},
                "assist": payload.get("assist") or {},
                "team": payload.get("team") or {},
                "side": (
                    "home" if str(team_id) == str(match.home_team_id)
                    else "away" if str(team_id) == str(match.away_team_id)
                    else "home" if home_team and team_name == home_team.name.casefold()
                    else "away" if away_team and team_name == away_team.name.casefold()
                    else None
                ),
                "collected_at": row.collected_at.isoformat(),
            })
        return sorted(
            result,
            key=lambda item: (
                int(item["minute"] or 0), int(item["extra"] or 0)
            ),
        )

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
        self,
        match_id: int | None = None,
        limit: int | None = None,
        top_per_market: int | None = None,
    ) -> list[dict]:
        home, away = aliased(Team), aliased(Team)
        ranked = None
        if top_per_market is not None:
            ranked = (
                select(
                    Prediction.id.label("prediction_id"),
                    func.row_number().over(
                        partition_by=(
                            Prediction.match_id,
                            Prediction.market_id,
                        ),
                        order_by=Prediction.probability.desc(),
                    ).label("market_rank"),
                )
                .subquery()
            )
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
        if ranked is not None:
            statement = statement.join(
                ranked, ranked.c.prediction_id == Prediction.id
            ).where(ranked.c.market_rank <= top_per_market)
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

    def paper_trading(self) -> dict:
        if not inspect(self.session.connection()).has_table("paper_bets"):
            return {"enabled": True, "status": "migration_pending", "metrics": {}, "recent": []}
        portfolio = self.session.scalar(
            select(PaperPortfolioRecord).where(PaperPortfolioRecord.active.is_(True))
            .order_by(PaperPortfolioRecord.created_at).limit(1)
        )
        learning = self.session.scalar(
            select(PaperLearningRunRecord).order_by(PaperLearningRunRecord.created_at.desc()).limit(1)
        )
        recent = self.session.scalars(
            select(PaperBetRecord).order_by(PaperBetRecord.recommended_at.desc()).limit(100)
        ).all()
        return {
            "enabled": True,
            "mode": "paper_only",
            "portfolio": ({
                "name": portfolio.name,
                "initial_balance": portfolio.initial_balance,
                "current_balance": portfolio.current_balance,
                "peak_balance": portfolio.peak_balance,
            } if portfolio else None),
            "metrics": learning.metrics if learning else {},
            "last_learning_at": learning.created_at.isoformat() if learning else None,
            "recent": [{
                "id": str(row.id), "match_id": row.match_id,
                "market": row.market, "selection": row.selection,
                "risk": row.risk, "odds": row.offered_odds,
                "stake": row.stake, "status": row.status,
                "profit": row.profit, "clv": row.clv,
                "recommended_at": row.recommended_at.isoformat(),
                "settled_at": row.settled_at.isoformat() if row.settled_at else None,
            } for row in recent],
        }

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
        opportunities: list[RecommendationOpportunityRecord] = []
        if latest_evaluation:
            base = select(
                RecommendationOpportunityRecord.id.label("opportunity_id"),
                func.row_number().over(
                    partition_by=RecommendationOpportunityRecord.match_id,
                    order_by=(
                        RecommendationOpportunityRecord.safe.desc(),
                        cast(
                            RecommendationOpportunityRecord.score,
                            Float,
                        ).desc(),
                        RecommendationOpportunityRecord.id.desc(),
                    ),
                ).label("match_rank"),
            ).where(
                RecommendationOpportunityRecord.evaluated_at
                == latest_evaluation
            )
            if primary_only and match_id is None:
                ranked = base.subquery()
                statement = (
                    select(RecommendationOpportunityRecord)
                    .join(
                        ranked,
                        ranked.c.opportunity_id
                        == RecommendationOpportunityRecord.id,
                    )
                    .where(ranked.c.match_rank == 1)
                    .order_by(
                        RecommendationOpportunityRecord.safe.desc(),
                        cast(
                            RecommendationOpportunityRecord.score,
                            Float,
                        ).desc(),
                    )
                )
                if limit is not None:
                    statement = statement.limit(limit)
                opportunities = list(self.session.scalars(statement).all())
            else:
                opportunities = list(self.session.scalars(
                    select(RecommendationOpportunityRecord).where(
                        RecommendationOpportunityRecord.evaluated_at
                        == latest_evaluation
                    )
                ).all())
        if primary_only and match_id is None and opportunities:
            return self._primary_opportunities(
                opportunities, limit=limit
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
        prediction_rows = self.predictions(
            match_id=match_id,
            limit=(
                None if match_id is not None or primary_only
                else max(2000, (limit or 500) * 8)
            ),
            top_per_market=2,
        )
        grouped: dict[tuple[int, int], list[dict]] = {}
        best: dict[tuple[int, int], dict] = {}
        for row in prediction_rows:
            key = (row["match_id"], row["market_id"])
            grouped.setdefault(key, []).append(row)
            current = best.get(key)
            if current is None or row["probability"] > current["probability"]:
                best[key] = row
        has_explanations = inspect(self.session.connection()).has_table(
            PredictionExplanationRecord.__tablename__
        )
        explanation_map = (
            {
                int(item.prediction_id): item
                for item in self.session.scalars(
                    select(PredictionExplanationRecord).where(
                        PredictionExplanationRecord.prediction_id.in_(
                            [str(row["id"]) for row in best.values()] or ["-1"]
                        )
                    )
                ).all()
            }
            if has_explanations else {}
        )
        result = []
        for row in best.values():
            explanation = explanation_map.get(row["id"])
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
                "calibrated_probability": (
                    opportunity.metrics.get("calibrated_probability")
                    if opportunity else row["probability"]
                ),
                "recommendation_tier": (
                    opportunity.metrics.get("recommendation_tier", "experimental")
                    if opportunity else "experimental"
                ),
                "selection_threshold": (
                    opportunity.metrics.get("selection_threshold")
                    if opportunity else None
                ),
                "selective_coverage": (
                    opportunity.metrics.get("selective_coverage")
                    if opportunity else None
                ),
                "ensemble_weights": (
                    opportunity.metrics.get("ensemble_weights", {})
                    if opportunity else {}
                ),
                "odds_movement": (
                    opportunity.metrics.get("odds_movement", {})
                    if opportunity else {}
                ),
                "calibration_segment": (
                    opportunity.metrics.get("calibration_segment")
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
                "model_trace": (
                    {
                        "model_name": explanation.model_name,
                        "model_version": explanation.model_version,
                        "data_cutoff_at": explanation.data_cutoff_at.isoformat(),
                        "favorable_factors": explanation.favorable_factors,
                        "adverse_factors": explanation.adverse_factors,
                        "decision": explanation.decision,
                    }
                    if explanation else None
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

    def _primary_opportunities(
        self,
        opportunities: list[RecommendationOpportunityRecord],
        *,
        limit: int | None,
    ) -> list[dict]:
        """Caminho enxuto para o painel global: uma sugestão por partida."""
        best: dict[int, RecommendationOpportunityRecord] = {}
        for item in opportunities:
            numeric_match_id = int(item.match_id)
            current = best.get(numeric_match_id)
            ranking = (
                {
                    "high_confidence": 3,
                    "statistical_value": 2,
                    "experimental": 1,
                }.get(str(item.metrics.get("recommendation_tier")), 0),
                int(item.safe),
                float(item.score or 0),
                float(item.metrics.get("probability") or 0),
            )
            current_ranking = (
                {
                    "high_confidence": 3,
                    "statistical_value": 2,
                    "experimental": 1,
                }.get(str(current.metrics.get("recommendation_tier")), 0),
                int(current.safe),
                float(current.score or 0),
                float(current.metrics.get("probability") or 0),
            ) if current else (-1, -1, -1.0, -1.0)
            if ranking > current_ranking:
                best[numeric_match_id] = item
        selected = list(best.items())
        selected.sort(key=lambda pair: pair[0])
        if limit is not None:
            selected = selected[:limit]
        match_ids = [match_id for match_id, _ in selected]
        home, away = aliased(Team), aliased(Team)
        match_rows = {
            match.id: (match, home_team, away_team, competition)
            for match, home_team, away_team, competition
            in self.session.execute(
                select(Match, home, away, Competition)
                .join(home, home.id == Match.home_team_id)
                .join(away, away.id == Match.away_team_id)
                .join(Competition, Competition.id == Match.competition_id)
                .where(Match.id.in_(match_ids or [-1]))
            ).all()
        }
        markets = {
            item.code: item
            for item in self.session.scalars(select(Market)).all()
        }
        result = []
        for numeric_match_id, opportunity in selected:
            match_row = match_rows.get(numeric_match_id)
            market = markets.get(opportunity.market)
            if match_row is None or market is None:
                continue
            match, home_team, away_team, competition = match_row
            metrics = opportunity.metrics
            actionable = bool(opportunity.safe)
            result.append({
                "id": 0,
                "match_id": match.id,
                "match": f"{home_team.name} x {away_team.name}",
                "competition": competition.name,
                "kickoff_at": iso_local(match.kickoff_at, self.timezone),
                "market_id": market.id,
                "market": market.name,
                "market_category": market.category,
                "selection": opportunity.selection,
                "display_selection": opportunity.selection,
                "probability": float(metrics.get("probability") or 0),
                "calibrated_probability": float(
                    metrics.get("calibrated_probability")
                    or metrics.get("probability") or 0
                ),
                "implied_probability": metrics.get("implied_probability"),
                "expected_value": metrics.get("expected_value"),
                "confidence": float(metrics.get("confidence") or 0),
                "evidence": (
                    "high" if float(metrics.get("confidence") or 0) >= .75
                    else "medium" if float(metrics.get("confidence") or 0) >= .55
                    else "low"
                ),
                "risk": opportunity.risk,
                "model": metrics.get("selected_model")
                    or metrics.get("model_version"),
                "no_bet": False,
                "is_primary_recommendation": True,
                "probability_margin": 0,
                "actionable": actionable,
                "recommendation_type": (
                    "value_bet" if actionable else "model_pick"
                ),
                "blocked_reasons": opportunity.blocked_reasons,
                "warnings": metrics.get("warnings", []),
                "recommendation_score": float(opportunity.score or 0),
                "probability_interval": metrics.get("probability_interval"),
                "conservative_expected_value":
                    metrics.get("conservative_expected_value"),
                "fractional_kelly": metrics.get("fractional_kelly"),
                "recommendation_tier": metrics.get(
                    "recommendation_tier", "experimental"
                ),
                "selection_threshold": metrics.get("selection_threshold"),
                "selective_coverage": metrics.get("selective_coverage"),
                "ensemble_weights": metrics.get("ensemble_weights", {}),
                "odds_movement": metrics.get("odds_movement", {}),
                "calibration_segment": metrics.get("calibration_segment"),
                "odds_age_hours": metrics.get("odds_age_hours"),
                "market_samples": metrics.get("market_samples"),
                "model_trace": None,
            })
        return result

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
        quota_record = self.session.scalar(
            select(RawProviderPayloadRecord)
            .where(
                RawProviderPayloadRecord.provider == "api_football",
                RawProviderPayloadRecord.resource == "quota",
            )
            .order_by(RawProviderPayloadRecord.collected_at.desc())
        )
        capability_map = {
            "api_football": [
                "fixtures", "live", "statistics", "odds", "events",
                "lineups", "injuries", "player_statistics",
                "team_statistics", "provider_predictions", "live_odds",
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
        active_providers = {
            name.strip()
            for name in os.getenv("ACTIVE_PROVIDERS", "").split(",")
            if name.strip()
        }
        for row in health_rows:
            if active_providers and row.provider not in active_providers:
                continue
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
            "api_football_quota": (
                {
                    **quota_record.payload,
                    "collected_at": quota_record.collected_at.isoformat(),
                }
                if quota_record else None
            ),
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
                    "warnings": latest.error_message,
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
                        RawProviderPayloadRecord.resource.in_((
                            "statistics_attempt", "backfill_statistics_attempt",
                        )),
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
            "platform": IntelligencePlatformService(self.session).status(),
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
