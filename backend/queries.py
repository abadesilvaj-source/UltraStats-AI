from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.models import (
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
        statement = (
            select(Match, home, away, Competition)
            .join(home, home.id == Match.home_team_id)
            .join(away, away.id == Match.away_team_id)
            .join(Competition, Competition.id == Match.competition_id)
            .where(Match.status.in_(statuses))
            .order_by(Match.kickoff_at)
            .offset(offset)
        )
        if limit is not None:
            statement = statement.limit(limit)
        rows = self.session.execute(statement).all()
        return [
            {
                "id": match.id,
                "external_id": match.external_id,
                "status": match.status,
                "kickoff_at": iso_local(match.kickoff_at, self.timezone),
                "timezone": self.timezone,
                "competition": {
                    "id": competition.id,
                    "name": competition.name,
                    "country": competition.country,
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
        return base

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
        return list(grouped.values())

    def predictions(self, match_id: int | None = None) -> list[dict]:
        home, away = aliased(Team), aliased(Team)
        statement = (
            select(Prediction, Match, Market, home, away, Competition)
            .join(Match, Match.id == Prediction.match_id)
            .join(Market, Market.id == Prediction.market_id)
            .join(home, home.id == Match.home_team_id)
            .join(away, away.id == Match.away_team_id)
            .join(Competition, Competition.id == Match.competition_id)
            .where(Match.status.in_(("scheduled", "in_progress")))
            .order_by(Match.kickoff_at, Prediction.expected_value.desc())
        )
        if match_id is not None:
            statement = statement.where(Match.id == match_id)
        return [
            {
                "id": p.id,
                "match_id": match.id,
                "match": f"{home_team.name} x {away_team.name}",
                "competition": competition.name,
                "kickoff_at": iso_local(match.kickoff_at, self.timezone),
                "market_id": market.id,
                "market": market.name,
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

    def recommendations(self) -> list[dict]:
        return [
            row for row in self.predictions()
            if row["expected_value"] is not None and row["expected_value"] > 0
        ]

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
        }
