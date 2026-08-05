from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import os
from statistics import mean

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Market, Match, MatchStatistics, Odd
from app.utils.market_evaluator import evaluate_market
from ultrastats_ai.infrastructure.database.models import (
    OddsSnapshotRecord,
    ModelBacktestRecord,
    PaperBetRecord,
    PaperLearningRunRecord,
    PaperPortfolioRecord,
    ProcessingTaskRecord,
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
        corrected = self.reconcile_corrections()
        metrics = self.metrics()
        trained = self._learn(settled, metrics)
        self.session.commit()
        return {"created": created, "settled": settled, "corrected": corrected,
                "trained": trained, "metrics": metrics}

    def _portfolio(self, *, lock: bool = False) -> PaperPortfolioRecord:
        name = os.getenv("PAPER_TRADING_PORTFOLIO", "automatic-shadow-v2")
        statement = select(PaperPortfolioRecord).where(PaperPortfolioRecord.name == name)
        if lock:
            statement = statement.with_for_update()
        row = self.session.scalar(statement)
        if row is None:
            # Preserva integralmente o experimento anterior, mas impede que novas
            # decisões ou saldos sejam misturados entre versões da política.
            for previous in self.session.scalars(
                select(PaperPortfolioRecord).where(PaperPortfolioRecord.active.is_(True))
            ).all():
                previous.active = False
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
        portfolio = self._portfolio(lock=True)
        limit = int(os.getenv("PAPER_TRADING_CREATION_BATCH_SIZE", "500"))
        lookback = self.now - timedelta(days=int(os.getenv("PAPER_TRADING_BACKFILL_DAYS", "14")))
        day_start = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_keys = {
            (row.match_id, row.market, row.selection.casefold())
            for row in self.session.scalars(
                select(PaperBetRecord).where(
                    PaperBetRecord.portfolio_id == portfolio.id,
                    PaperBetRecord.recommended_at >= day_start
                )
            ).all()
        }
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
        pending_exposure = float(self.session.scalar(
            select(func.coalesce(func.sum(PaperBetRecord.stake), 0.0)).where(
                PaperBetRecord.portfolio_id == portfolio.id,
                PaperBetRecord.status == "pending",
            )
        ) or 0.0)
        daily_exposure = float(self.session.scalar(
            select(func.coalesce(func.sum(PaperBetRecord.stake), 0.0)).where(
                PaperBetRecord.portfolio_id == portfolio.id,
                PaperBetRecord.recommended_at >= day_start,
            )
        ) or 0.0)
        available_balance = max(0.0, portfolio.current_balance - pending_exposure)
        daily_cap = max(0.0, portfolio.current_balance * float(
            os.getenv("PAPER_TRADING_DAILY_EXPOSURE", "0.03")
        ))
        match_cap_fraction = float(os.getenv("PAPER_TRADING_MATCH_EXPOSURE", "0.01"))
        competition_cap_fraction = float(os.getenv("PAPER_TRADING_COMPETITION_EXPOSURE", "0.015"))
        market_cap_fraction = float(os.getenv("PAPER_TRADING_MARKET_EXPOSURE", "0.015"))
        correlation_cap_fraction = float(os.getenv("PAPER_TRADING_CORRELATION_EXPOSURE", "0.01"))
        minimum_odds = float(os.getenv("PAPER_TRADING_MIN_ODDS", "1.60"))
        maximum_odds = float(os.getenv("PAPER_TRADING_MAX_ODDS", "2.99"))
        minimum_probability = float(os.getenv("PAPER_TRADING_MIN_PROBABILITY", "0.80"))
        maximum_horizon = float(os.getenv("PAPER_TRADING_MAX_HORIZON_HOURS", "6"))
        blocked_markets = {
            item.strip() for item in os.getenv(
                "PAPER_TRADING_BLOCKED_MARKETS",
                "correct_score,over_3_5_goals,over_4_5_goals,over_5_5_goals,"
                "under_0_5_goals,home_over_3_5_goals,away_over_3_5_goals,"
                "corners,home_corners,away_corners",
            ).split(",") if item.strip()
        }
        executable_markets = {
            item.strip() for item in os.getenv(
                "PAPER_TRADING_EXECUTABLE_MARKETS",
                "under_2_5_goals,under_3_5_goals,both_teams_to_score",
            ).split(",") if item.strip()
        }
        today_bets = self.session.scalars(select(PaperBetRecord).where(
            PaperBetRecord.portfolio_id == portfolio.id,
            PaperBetRecord.recommended_at >= day_start,
        )).all()
        competition_exposure: dict[str, float] = defaultdict(float)
        market_exposure: dict[str, float] = defaultdict(float)
        correlation_exposure: dict[str, float] = defaultdict(float)
        for row in today_bets:
            competition_exposure[str(row.competition_id)] += row.stake
            market_exposure[row.market] += row.stake
            correlation_exposure[str((row.snapshot or {}).get("correlation_key"))] += row.stake
        breaker = self._circuit_breaker(portfolio)
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
            daily_key = (
                opportunity.match_id,
                opportunity.market,
                opportunity.selection.casefold(),
            )
            if daily_key in daily_keys:
                continue
            recommended = self._aware(opportunity.evaluated_at)
            kickoff = self._aware(match.kickoff_at)
            if recommended >= kickoff:
                continue
            metrics = opportunity.metrics or {}
            probability_interval = metrics.get("probability_interval") or {}
            probability = float(
                probability_interval.get("low")
                or metrics.get("calibrated_probability")
                or metrics.get("probability") or 0
            )
            if not 0 < probability < 1:
                continue
            tier = str(metrics.get("recommendation_tier") or "unknown")
            horizon_hours = max(0.0, (kickoff - recommended).total_seconds() / 3600)
            odds_age_hours = float(metrics.get("odds_age_hours") or 0)
            maximum_odds_age = float(os.getenv("PAPER_TRADING_MAX_ODDS_AGE_HOURS", "0.5"))
            expires_at = min(kickoff, recommended + timedelta(hours=maximum_odds_age))
            minimum_edge = float(os.getenv("PAPER_TRADING_MIN_PRICE_EDGE", "0.03"))
            minimum_valid_odds = round((1 + minimum_edge) / probability, 3)
            price_is_valid = (
                odds >= minimum_valid_odds
                and odds_age_hours <= maximum_odds_age
                and self.now <= expires_at
            )
            observed_risk = self._observed_risk(
                portfolio.id, str(match.competition_id), opportunity.market,
                fallback=opportunity.risk,
            )
            executable = (
                tier == "high_confidence"
                and opportunity.market in executable_markets
                and minimum_odds <= odds <= maximum_odds
                and probability >= minimum_probability
                and horizon_hours <= maximum_horizon
                and opportunity.market not in blocked_markets
                and "corner" not in opportunity.market
                and available_balance > 0
                and daily_exposure < daily_cap
                and price_is_valid
                and not breaker["open"]
            )
            match_exposure = float(self.session.scalar(
                select(func.coalesce(func.sum(PaperBetRecord.stake), 0.0)).where(
                    PaperBetRecord.portfolio_id == portfolio.id,
                    PaperBetRecord.match_id == opportunity.match_id,
                    PaperBetRecord.status == "pending",
                )
            ) or 0.0)
            match_cap = max(0.0, portfolio.current_balance * match_cap_fraction)
            competition_cap = portfolio.current_balance * competition_cap_fraction
            market_cap = portfolio.current_balance * market_cap_fraction
            correlation_cap = portfolio.current_balance * correlation_cap_fraction
            correlation_key = opportunity.correlation_key
            kelly = max(0.0, (probability * odds - 1) / (odds - 1))
            desired_stake = portfolio.current_balance * min(.005, kelly * .10)
            stake = round(max(0.0, min(
                desired_stake,
                available_balance,
                daily_cap - daily_exposure,
                match_cap - match_exposure,
                competition_cap - competition_exposure[str(match.competition_id)],
                market_cap - market_exposure[opportunity.market],
                correlation_cap - correlation_exposure[correlation_key],
            )), 2) if executable else 0.0
            executable = executable and stake >= .01
            if not executable:
                stake = 0.0
            snapshot = {
                "metrics": metrics,
                "blocked_reasons": opportunity.blocked_reasons,
                "explanation": opportunity.explanation,
                "bookmaker": opportunity.bookmaker,
                "mode": "paper_executed" if executable else "shadow_observation",
                "policy": "selective_reserved_exposure_v2",
                "recommendation_tier": tier,
                "execution_probability": probability,
                "horizon_hours": round(horizon_hours, 3),
                "correlation_key": correlation_key,
                "minimum_valid_odds": minimum_valid_odds,
                "odds_age_hours": odds_age_hours,
                "expires_at": expires_at.isoformat(),
                "price_is_valid": price_is_valid,
                "circuit_breaker": breaker,
                "observed_risk": observed_risk,
                "exposure_limits": {
                    "daily": daily_cap, "match": match_cap,
                    "competition": competition_cap, "market": market_cap,
                    "correlation": correlation_cap,
                },
            }
            self.session.add(PaperBetRecord(
                portfolio_id=portfolio.id, opportunity_id=opportunity.id,
                match_id=opportunity.match_id, competition_id=str(match.competition_id),
                market=opportunity.market, selection=opportunity.selection,
                risk=str(observed_risk["label"]), offered_odds=odds, probability=probability,
                stake=stake, payout=0.0, profit=0.0, status="pending",
                snapshot=snapshot, recommended_at=recommended, kickoff_at=kickoff,
            ))
            daily_keys.add(daily_key)
            if executable:
                available_balance -= stake
                daily_exposure += stake
                competition_exposure[str(match.competition_id)] += stake
                market_exposure[opportunity.market] += stake
                correlation_exposure[correlation_key] += stake
            created += 1
        self.session.flush()
        return created

    def settle_finished(self) -> int:
        self._portfolio()
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
            bet.snapshot = {
                **(bet.snapshot or {}),
                "result_signature": self._result_signature(match, stats),
            }
            portfolio = self.session.get(PaperPortfolioRecord, bet.portfolio_id)
            if portfolio is not None and bet.stake > 0:
                portfolio.current_balance += bet.profit
                portfolio.peak_balance = max(portfolio.peak_balance, portfolio.current_balance)
                portfolio.updated_at = self.now
            settled += 1
        self.session.flush()
        return settled

    def reconcile_corrections(self) -> int:
        """Reprocessa correções oficiais sem duplicar lucro ou apagar evidência."""
        bets = self.session.scalars(
            select(PaperBetRecord).where(
                PaperBetRecord.status.in_(("won", "lost", "void")),
                PaperBetRecord.settled_at >= self.now - timedelta(days=14),
            ).limit(2000)
        ).all()
        corrected = 0
        affected_portfolios: set[object] = set()
        for bet in bets:
            match = self.session.get(Match, int(bet.match_id)) if bet.match_id.isdigit() else None
            if match is None or match.status not in {"finished", "completed", "ended"}:
                continue
            stats = self.session.scalar(select(MatchStatistics).where(
                MatchStatistics.match_id == match.id
            ))
            signature = self._result_signature(match, stats)
            previous = (bet.snapshot or {}).get("result_signature")
            if previous is None:
                bet.snapshot = {**(bet.snapshot or {}), "result_signature": signature}
                continue
            if previous == signature:
                continue
            try:
                result = evaluate_market(
                    bet.market, bet.selection, int(match.home_score or 0),
                    int(match.away_score or 0),
                    getattr(stats, "corners_home", None), getattr(stats, "corners_away", None),
                    getattr(stats, "yellow_cards_home", None), getattr(stats, "yellow_cards_away", None),
                    getattr(stats, "red_cards_home", None), getattr(stats, "red_cards_away", None),
                )
            except ValueError:
                continue
            if result == "unsupported":
                continue
            old_status = bet.status
            bet.status = result
            bet.payout = bet.stake * bet.offered_odds if result == "won" else bet.stake if result == "void" else 0.0
            bet.profit = bet.payout - bet.stake
            bet.settled_at = self.now
            bet.snapshot = {
                **(bet.snapshot or {}), "result_signature": signature,
                "correction": {"from": old_status, "to": result, "at": self.now.isoformat()},
            }
            affected_portfolios.add(bet.portfolio_id)
            corrected += 1
        for portfolio_id in affected_portfolios:
            self._recompute_portfolio(portfolio_id)
        self.session.flush()
        return corrected

    def _recompute_portfolio(self, portfolio_id) -> None:
        portfolio = self.session.get(PaperPortfolioRecord, portfolio_id)
        if portfolio is None:
            return
        rows = self.session.scalars(select(PaperBetRecord).where(
            PaperBetRecord.portfolio_id == portfolio_id,
            PaperBetRecord.stake > 0,
            PaperBetRecord.status.in_(("won", "lost", "void")),
        ).order_by(PaperBetRecord.settled_at, PaperBetRecord.id)).all()
        balance = peak = portfolio.initial_balance
        for row in rows:
            balance += row.profit
            peak = max(peak, balance)
        portfolio.current_balance = balance
        portfolio.peak_balance = peak
        portfolio.updated_at = self.now

    def _circuit_breaker(self, portfolio: PaperPortfolioRecord) -> dict[str, object]:
        drawdown = ((portfolio.peak_balance - portfolio.current_balance) /
                    portfolio.peak_balance if portfolio.peak_balance else 0.0)
        reasons = []
        if drawdown >= float(os.getenv("PAPER_TRADING_MAX_DRAWDOWN", "0.10")):
            reasons.append("drawdown_limit")
        latest = self.session.scalar(select(ModelBacktestRecord).where(
            ModelBacktestRecord.model_name == "g37_mlops_governance"
        ).order_by(ModelBacktestRecord.evaluated_at.desc()))
        drift = (latest.metrics or {}).get("drift", {}) if latest else {}
        for kind in ("data", "calibration", "coverage"):
            if (drift.get(kind) or {}).get("detected"):
                reasons.append(f"{kind}_drift")
        return {"open": bool(reasons), "reasons": reasons,
                "drawdown": round(drawdown, 6), "checked_at": self.now.isoformat()}

    def _observed_risk(self, portfolio_id, competition_id: str, market: str,
                       *, fallback: str) -> dict[str, object]:
        rows = self.session.scalars(select(PaperBetRecord).where(
            PaperBetRecord.portfolio_id == portfolio_id,
            PaperBetRecord.competition_id == competition_id,
            PaperBetRecord.market == market,
            PaperBetRecord.status.in_(("won", "lost")),
        ).order_by(PaperBetRecord.settled_at.desc()).limit(250)).all()
        if len(rows) < int(os.getenv("PAPER_RISK_MIN_SAMPLES", "30")):
            return {"label": fallback, "samples": len(rows), "loss_rate": None,
                    "source": "provisional_fallback"}
        loss_rate = sum(row.status == "lost" for row in rows) / len(rows)
        label = "low" if loss_rate <= .20 else "moderate" if loss_rate <= .35 else "high"
        return {"label": label, "samples": len(rows),
                "loss_rate": round(loss_rate, 6), "source": "observed_settlements"}

    @staticmethod
    def _result_signature(match: Match, stats: MatchStatistics | None) -> str:
        values = (
            match.home_score, match.away_score,
            getattr(stats, "corners_home", None), getattr(stats, "corners_away", None),
            getattr(stats, "yellow_cards_home", None), getattr(stats, "yellow_cards_away", None),
            getattr(stats, "red_cards_home", None), getattr(stats, "red_cards_away", None),
        )
        return "|".join("" if value is None else str(value) for value in values)

    def metrics(self) -> dict[str, object]:
        portfolio = self._portfolio()
        bets = self.session.scalars(select(PaperBetRecord).where(
            PaperBetRecord.portfolio_id == portfolio.id,
            PaperBetRecord.status.in_(("won", "lost", "void")),
        )).all()
        executed = [row for row in bets if row.stake > 0]
        stake = sum(row.stake for row in bets)
        profit = sum(row.profit for row in bets)
        segments: dict[str, list[PaperBetRecord]] = defaultdict(list)
        risk_segments: dict[str, list[PaperBetRecord]] = defaultdict(list)
        player_groups: dict[str, list[PaperBetRecord]] = defaultdict(list)
        cohorts: dict[str, list[PaperBetRecord]] = defaultdict(list)
        for row in bets:
            segments[f"{row.competition_id}:{row.market}"].append(row)
            risk_segments[row.risk].append(row)
            metrics = (row.snapshot or {}).get("metrics", {})
            player_context = metrics.get("player_impact") or metrics.get("player_context")
            player_groups["with_player_context" if player_context else "without_player_context"].append(row)
            mode = str((row.snapshot or {}).get("mode") or "paper_only")
            policy = str((row.snapshot or {}).get("policy") or "legacy")
            cohorts[f"{policy}:{mode}"].append(row)
        minimum = int(os.getenv("PAPER_POLICY_MIN_SEGMENT_SAMPLES", "100"))
        breaker = self._circuit_breaker(portfolio)
        exposure_audit = self._exposure_audit(portfolio)
        return {
            "portfolio_name": portfolio.name,
            "settled": len(bets), "executed_settled": len(executed),
            "shadow_settled": len(bets) - len(executed),
            "stake": round(stake, 2), "profit": round(profit, 2),
            "paper_roi": round(profit / stake, 6) if stake else None,
            "mean_clv": round(mean([row.clv for row in bets if row.clv is not None]), 6) if any(row.clv is not None for row in bets) else None,
            "paper_brier_score": round(mean((row.probability - int(row.status == "won")) ** 2 for row in bets), 6) if bets else None,
            "balance": round(portfolio.current_balance, 2),
            "paper_drawdown": round((portfolio.peak_balance - portfolio.current_balance) / portfolio.peak_balance, 6) if portfolio.peak_balance else 0,
            "simulation_started_at": portfolio.created_at.isoformat(),
            "simulation_days": max(0, (self.now - self._aware(portfolio.created_at)).days),
            "circuit_breaker": breaker,
            "exposure_audit": exposure_audit,
            "g38_gates": {
                "transactional_reservation": True,
                "aggregate_exposure_within_limits": exposure_audit["passed"],
                "no_stake_without_fresh_price": exposure_audit["fresh_price_passed"],
                "corrections_are_reconcilable": True,
                "promotion_requires_roi_clv_calibration": True,
            },
            "cohorts": {
                key: self._cohort_metrics(rows) for key, rows in cohorts.items()
            },
            "risk_review": {
                key: {"samples": len(rows), "executed": sum(row.stake > 0 for row in rows),
                      "paper_roi": (round(sum(row.profit for row in rows) / sum(row.stake for row in rows), 6)
                              if sum(row.stake for row in rows) else None)}
                for key, rows in risk_segments.items()
            },
            "player_impact_ablation": {
                key: {"samples": len(rows), "brier_score": round(mean((row.probability - int(row.status == "won")) ** 2 for row in rows), 6)}
                for key, rows in player_groups.items()
            },
            "segments": {
                key: {
                    "samples": len(rows),
                    "executed": sum(row.stake > 0 for row in rows),
                    "hit_rate": round(sum(row.status == "won" for row in rows) / len(rows), 6),
                    "brier_score": round(mean(
                        (row.probability - int(row.status == "won")) ** 2 for row in rows
                    ), 6),
                    "paper_roi": (
                        round(sum(row.profit for row in rows) / sum(row.stake for row in rows), 6)
                        if sum(row.stake for row in rows) else None
                    ),
                    "eligible_for_policy": (
                        len(rows) >= minimum
                        and sum(row.stake for row in rows) > 0
                        and sum(row.profit for row in rows) > 0
                        and any(row.clv is not None for row in rows)
                        and mean(row.clv for row in rows if row.clv is not None) >= 0
                        and mean((row.probability - int(row.status == "won")) ** 2 for row in rows) <= .20
                        and not breaker["open"]
                    ),
                    "promotion_gate_failures": self._promotion_failures(rows, minimum, breaker),
                }
                for key, rows in segments.items() if rows
            },
        }

    def _exposure_audit(self, portfolio: PaperPortfolioRecord) -> dict[str, object]:
        day_start = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
        rows = self.session.scalars(select(PaperBetRecord).where(
            PaperBetRecord.portfolio_id == portfolio.id,
            PaperBetRecord.recommended_at >= day_start,
            PaperBetRecord.stake > 0,
        )).all()
        balance = max(1.0, portfolio.current_balance)
        dimensions = {
            "daily": ({"all": rows}, float(os.getenv("PAPER_TRADING_DAILY_EXPOSURE", ".03"))),
            "match": (self._group_bets(rows, lambda row: row.match_id), float(os.getenv("PAPER_TRADING_MATCH_EXPOSURE", ".01"))),
            "competition": (self._group_bets(rows, lambda row: str(row.competition_id)), float(os.getenv("PAPER_TRADING_COMPETITION_EXPOSURE", ".015"))),
            "market": (self._group_bets(rows, lambda row: row.market), float(os.getenv("PAPER_TRADING_MARKET_EXPOSURE", ".015"))),
            "correlation": (self._group_bets(rows, lambda row: str((row.snapshot or {}).get("correlation_key"))), float(os.getenv("PAPER_TRADING_CORRELATION_EXPOSURE", ".01"))),
        }
        violations = []
        for dimension, (groups, cap) in dimensions.items():
            for key, items in groups.items():
                exposure = sum(row.stake for row in items) / balance
                if exposure > cap + 1e-9:
                    violations.append({"dimension": dimension, "key": key,
                                       "exposure": exposure, "cap": cap})
        fresh_price_passed = all(
            bool((row.snapshot or {}).get("price_is_valid"))
            for row in rows
            if (row.snapshot or {}).get("policy") == "selective_reserved_exposure_v2"
        )
        return {"passed": not violations, "fresh_price_passed": fresh_price_passed,
                "executed_today": len(rows), "violations": violations,
                "concurrency_control": "portfolio_row_for_update"}

    @staticmethod
    def _group_bets(rows: list[PaperBetRecord], key):
        grouped: dict[str, list[PaperBetRecord]] = defaultdict(list)
        for row in rows:
            grouped[str(key(row))].append(row)
        return grouped

    @staticmethod
    def _cohort_metrics(rows: list[PaperBetRecord]) -> dict[str, object]:
        decisions = [row for row in rows if row.status in {"won", "lost"}]
        executed = [row for row in rows if row.stake > 0]
        total_stake = sum(row.stake for row in executed)
        profit = sum(row.profit for row in executed)
        equity = peak = max_drawdown = 0.0
        for row in sorted(executed, key=lambda item: (item.settled_at or item.kickoff_at, str(item.id))):
            equity += row.profit
            peak = max(peak, equity)
            max_drawdown = max(max_drawdown, peak - equity)
        clv = [row.clv for row in rows if row.clv is not None]
        return {
            "samples": len(rows), "executed": len(executed),
            "hit_rate": round(sum(row.status == "won" for row in decisions) / len(decisions), 6) if decisions else None,
            "brier_score": round(mean((row.probability - int(row.status == "won")) ** 2 for row in decisions), 6) if decisions else None,
            "mean_clv": round(mean(clv), 6) if clv else None,
            "roi": round(profit / total_stake, 6) if total_stake else None,
            "yield": round(profit / total_stake, 6) if total_stake else None,
            "max_drawdown_units": round(max_drawdown, 2),
            "max_drawdown_fraction": round(max_drawdown / max(1.0, peak), 6),
        }

    @staticmethod
    def _promotion_failures(rows: list[PaperBetRecord], minimum: int,
                            breaker: dict[str, object]) -> list[str]:
        failures = []
        stake = sum(row.stake for row in rows)
        profit = sum(row.profit for row in rows)
        clv = [row.clv for row in rows if row.clv is not None]
        decisions = [row for row in rows if row.status in {"won", "lost"}]
        brier = mean((row.probability - int(row.status == "won")) ** 2 for row in decisions) if decisions else 1.0
        if len(rows) < minimum: failures.append("insufficient_samples")
        if stake <= 0 or profit / stake <= 0: failures.append("non_positive_roi")
        if not clv or mean(clv) < 0: failures.append("negative_or_missing_clv")
        if brier > .20: failures.append("calibration_degraded")
        if breaker["open"]: failures.append("circuit_breaker_open")
        return failures

    def _learn(self, newly_settled: int, metrics: dict[str, object]) -> bool:
        threshold = int(os.getenv("PAPER_ML_RETRAIN_SETTLEMENTS", "100"))
        last = self.session.scalar(select(PaperLearningRunRecord).order_by(PaperLearningRunRecord.created_at.desc()).limit(1))
        previous = int((last.metrics or {}).get("settled", 0)) if last else 0
        should_train = newly_settled > 0 and int(metrics["settled"]) - previous >= threshold
        if should_train:
            # O modelo aprende com features anteriores ao jogo e placar posterior;
            # o resultado da aposta governa políticas, sem duplicar o rótulo.
            settled_bucket = int(metrics["settled"]) // threshold
            key = f"model-training:paper:{settled_bucket}"
            if self.session.scalar(select(ProcessingTaskRecord.id).where(
                ProcessingTaskRecord.idempotency_key == key
            )) is None:
                self.session.add(ProcessingTaskRecord(
                    kind="model_training", idempotency_key=key,
                    payload={"trigger": "paper_settlement", "settled": metrics["settled"]},
                    status="pending", priority=20, attempts=0, max_attempts=3,
                    available_at=self.now, created_at=self.now,
                ))
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
