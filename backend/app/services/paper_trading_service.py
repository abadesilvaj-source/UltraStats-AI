from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import os
from statistics import mean

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Market, Match, MatchStatistics, Odd
from app.services.temporal_ml_service import TemporalMLService
from app.utils.market_evaluator import evaluate_market
from ultrastats_ai.infrastructure.database.models import (
    OddsSnapshotRecord,
    PaperBetRecord,
    PaperLearningRunRecord,
    PaperPortfolioRecord,
    RecommendationOpportunityRecord,
)


class PaperTradingService:
    """Executa o ciclo automático de apostas fictícias sem acessar banca real."""

    def __init__(self, session: Session, *, now: datetime | None = None) -> None:
        self.session = session
        self.now = now or datetime.now(timezone.utc)

    def run(self) -> dict[str, object]:
        created = self.create_pending()
        settled = self.settle_finished()
        metrics = self.metrics()
        trained = self._learn(settled, metrics)
        self.session.commit()
        return {"created": created, "settled": settled, "trained": trained, "metrics": metrics}

    def _portfolio(self) -> PaperPortfolioRecord:
        name = os.getenv("PAPER_TRADING_PORTFOLIO", "automatic-shadow-v1")
        row = self.session.scalar(select(PaperPortfolioRecord).where(PaperPortfolioRecord.name == name))
        if row is None:
            balance = float(os.getenv("PAPER_TRADING_INITIAL_BALANCE", "10000"))
            row = PaperPortfolioRecord(
                name=name, initial_balance=balance, current_balance=balance,
                peak_balance=balance, currency="BRL", active=True,
                created_at=self.now, updated_at=self.now,
            )
            self.session.add(row)
            self.session.flush()
        return row

    def create_pending(self) -> int:
        portfolio = self._portfolio()
        limit = int(os.getenv("PAPER_TRADING_CREATION_BATCH_SIZE", "500"))
        lookback = self.now - timedelta(days=int(os.getenv("PAPER_TRADING_BACKFILL_DAYS", "14")))
        existing = select(PaperBetRecord.opportunity_id)
        opportunities = self.session.scalars(
            select(RecommendationOpportunityRecord)
            .where(
                RecommendationOpportunityRecord.safe.is_(True),
                RecommendationOpportunityRecord.offered_odds.is_not(None),
                RecommendationOpportunityRecord.evaluated_at >= lookback,
                RecommendationOpportunityRecord.id.not_in(existing),
            )
            .order_by(RecommendationOpportunityRecord.evaluated_at)
            .limit(limit)
        ).all()
        created = 0
        for opportunity in opportunities:
            try:
                match_id = int(opportunity.match_id)
                odds = float(opportunity.offered_odds or 0)
            except (TypeError, ValueError):
                continue
            match = self.session.get(Match, match_id)
            if match is None or odds <= 1.0:
                continue
            recommended = self._aware(opportunity.evaluated_at)
            kickoff = self._aware(match.kickoff_at)
            if recommended >= kickoff:
                continue
            metrics = opportunity.metrics or {}
            probability = float(metrics.get("calibrated_probability") or metrics.get("probability") or 0)
            if not 0 < probability < 1:
                continue
            kelly = max(0.0, (probability * odds - 1) / (odds - 1))
            risk_cap = {"low": .01, "moderate": .005, "high": .0025}.get(opportunity.risk, .0025)
            fraction = min(risk_cap, kelly * .25)
            stake = round(max(.01, portfolio.current_balance * fraction), 2)
            stake = min(stake, max(.01, portfolio.current_balance * .01))
            snapshot = {
                "metrics": metrics,
                "blocked_reasons": opportunity.blocked_reasons,
                "explanation": opportunity.explanation,
                "bookmaker": opportunity.bookmaker,
                "mode": "paper_only",
                "policy": "fractional_kelly_risk_capped_v1",
            }
            self.session.add(PaperBetRecord(
                portfolio_id=portfolio.id, opportunity_id=opportunity.id,
                match_id=opportunity.match_id, competition_id=str(match.competition_id),
                market=opportunity.market, selection=opportunity.selection,
                risk=opportunity.risk, offered_odds=odds, probability=probability,
                stake=stake, payout=0.0, profit=0.0, status="pending",
                snapshot=snapshot, recommended_at=recommended, kickoff_at=kickoff,
            ))
            created += 1
        self.session.flush()
        return created

    def settle_finished(self) -> int:
        portfolio = self._portfolio()
        limit = int(os.getenv("PAPER_TRADING_SETTLEMENT_BATCH_SIZE", "500"))
        bets = self.session.scalars(
            select(PaperBetRecord).where(PaperBetRecord.status == "pending")
            .order_by(PaperBetRecord.kickoff_at).limit(limit)
        ).all()
        settled = 0
        for bet in bets:
            try:
                match = self.session.get(Match, int(bet.match_id))
            except ValueError:
                continue
            if match is None or match.status not in {"finished", "completed", "ended"}:
                continue
            stats = self.session.scalar(select(MatchStatistics).where(MatchStatistics.match_id == match.id))
            try:
                result = evaluate_market(
                    bet.market, bet.selection, int(match.home_score or 0), int(match.away_score or 0),
                    getattr(stats, "corners_home", None), getattr(stats, "corners_away", None),
                    getattr(stats, "yellow_cards_home", None), getattr(stats, "yellow_cards_away", None),
                    getattr(stats, "red_cards_home", None), getattr(stats, "red_cards_away", None),
                )
            except ValueError:
                continue
            if result == "unsupported":
                bet.status, bet.settled_at = "unsupported", self.now
                continue
            closing = self.session.scalar(
                select(OddsSnapshotRecord.decimal_odds)
                .where(
                    OddsSnapshotRecord.match_id == bet.match_id,
                    OddsSnapshotRecord.market == bet.market,
                    func.lower(OddsSnapshotRecord.selection) == bet.selection.lower(),
                    OddsSnapshotRecord.captured_at <= bet.kickoff_at,
                ).order_by(OddsSnapshotRecord.captured_at.desc()).limit(1)
            )
            if closing is None:
                closing = self.session.scalar(
                    select(Odd.odd_value).join(Market, Market.id == Odd.market_id)
                    .where(
                        Odd.match_id == match.id,
                        Market.code == bet.market,
                        func.lower(Odd.selection) == bet.selection.lower(),
                        Odd.collected_at <= bet.kickoff_at.replace(tzinfo=None),
                    ).order_by(Odd.collected_at.desc()).limit(1)
                )
            try:
                bet.closing_odds = float(closing) if closing else None
            except (TypeError, ValueError):
                bet.closing_odds = None
            bet.clv = (
                bet.offered_odds / bet.closing_odds - 1
                if bet.closing_odds and bet.closing_odds > 1 else None
            )
            bet.payout = bet.stake * bet.offered_odds if result == "won" else bet.stake if result == "void" else 0.0
            bet.profit = bet.payout - bet.stake
            bet.status, bet.settled_at = result, self.now
            portfolio.current_balance += bet.profit
            portfolio.peak_balance = max(portfolio.peak_balance, portfolio.current_balance)
            portfolio.updated_at = self.now
            settled += 1
        self.session.flush()
        return settled

    def metrics(self) -> dict[str, object]:
        portfolio = self._portfolio()
        bets = self.session.scalars(select(PaperBetRecord).where(PaperBetRecord.status.in_(("won", "lost", "void")))).all()
        stake = sum(row.stake for row in bets)
        profit = sum(row.profit for row in bets)
        segments: dict[str, list[PaperBetRecord]] = defaultdict(list)
        risk_segments: dict[str, list[PaperBetRecord]] = defaultdict(list)
        player_groups: dict[str, list[PaperBetRecord]] = defaultdict(list)
        for row in bets:
            segments[f"{row.competition_id}:{row.market}"].append(row)
            risk_segments[row.risk].append(row)
            metrics = (row.snapshot or {}).get("metrics", {})
            player_context = metrics.get("player_impact") or metrics.get("player_context")
            player_groups["with_player_context" if player_context else "without_player_context"].append(row)
        minimum = int(os.getenv("PAPER_POLICY_MIN_SEGMENT_SAMPLES", "100"))
        return {
            "settled": len(bets), "stake": round(stake, 2), "profit": round(profit, 2),
            "roi": round(profit / stake, 6) if stake else None,
            "mean_clv": round(mean([row.clv for row in bets if row.clv is not None]), 6) if any(row.clv is not None for row in bets) else None,
            "brier": round(mean((row.probability - int(row.status == "won")) ** 2 for row in bets), 6) if bets else None,
            "balance": round(portfolio.current_balance, 2),
            "drawdown": round((portfolio.peak_balance - portfolio.current_balance) / portfolio.peak_balance, 6) if portfolio.peak_balance else 0,
            "simulation_started_at": portfolio.created_at.isoformat(),
            "simulation_days": max(0, (self.now - self._aware(portfolio.created_at)).days),
            "risk_review": {
                key: {"samples": len(rows), "roi": round(sum(row.profit for row in rows) / sum(row.stake for row in rows), 6)}
                for key, rows in risk_segments.items()
            },
            "player_impact_ablation": {
                key: {"samples": len(rows), "brier": round(mean((row.probability - int(row.status == "won")) ** 2 for row in rows), 6)}
                for key, rows in player_groups.items()
            },
            "segments": {
                key: {"samples": len(rows), "eligible_for_policy": len(rows) >= minimum,
                      "roi": round(sum(row.profit for row in rows) / sum(row.stake for row in rows), 6)}
                for key, rows in segments.items() if rows
            },
        }

    def _learn(self, newly_settled: int, metrics: dict[str, object]) -> bool:
        threshold = int(os.getenv("PAPER_ML_RETRAIN_SETTLEMENTS", "100"))
        last = self.session.scalar(select(PaperLearningRunRecord).order_by(PaperLearningRunRecord.created_at.desc()).limit(1))
        previous = int((last.metrics or {}).get("settled", 0)) if last else 0
        should_train = newly_settled > 0 and int(metrics["settled"]) - previous >= threshold
        if should_train:
            # O modelo aprende com features anteriores ao jogo e placar posterior;
            # o resultado da aposta governa políticas, sem duplicar o rótulo.
            TemporalMLService(self.session, force_retraining=True)._load_or_train()
        eligible = [
            {"segment": key, **value} for key, value in metrics.get("segments", {}).items()
            if value.get("eligible_for_policy")
        ]
        if newly_settled or last is None:
            self.session.add(PaperLearningRunRecord(
                metrics=metrics, policy_updates=eligible,
                model_training_triggered=should_train, created_at=self.now,
            ))
        return should_train

    @staticmethod
    def _aware(value: datetime) -> datetime:
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
