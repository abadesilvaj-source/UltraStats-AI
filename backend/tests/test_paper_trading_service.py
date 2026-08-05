from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Competition, Match, MatchStatistics, Team
from app.services.paper_trading_service import PaperTradingService
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase, PaperBetRecord, PaperPortfolioRecord,
    RecommendationOpportunityRecord,
)


def _session() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    CanonicalBase.metadata.create_all(engine)
    return Session(engine)


def _scenario(session: Session, now: datetime):
    competition = Competition(name="Paper League", country="BR")
    home, away = Team(name="Home"), Team(name="Away")
    session.add_all((competition, home, away))
    session.flush()
    match = Match(
        competition_id=competition.id, home_team_id=home.id, away_team_id=away.id,
        kickoff_at=(now + timedelta(hours=2)).replace(tzinfo=None), status="scheduled",
    )
    session.add(match)
    session.flush()
    opportunity = RecommendationOpportunityRecord(
        match_id=str(match.id), market="under_2_5_goals", selection="Under 2.5",
        bookmaker="paper", offered_odds="2.00",
        metrics={
            "probability": .84, "calibrated_probability": .84,
            "probability_interval": {"low": .82, "high": .88},
            "recommendation_tier": "high_confidence",
        },
        risk="low", score="0.8", safe=True, blocked_reasons=[], explanation=[],
        correlation_key=f"{match.id}:goals", evaluated_at=now,
    )
    session.add(opportunity)
    session.commit()
    return match, opportunity


def test_cycle_is_idempotent_and_never_creates_user_bankroll():
    now = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
    session = _session()
    _scenario(session, now)

    first = PaperTradingService(session, now=now).run()
    second = PaperTradingService(session, now=now).run()

    assert first["created"] == 1
    assert second["created"] == 0
    assert session.scalar(select(PaperBetRecord)).status == "pending"
    assert session.scalar(select(PaperPortfolioRecord)).current_balance == 10000


def test_finished_match_is_settled_and_becomes_learning_evidence(monkeypatch):
    now = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
    session = _session()
    match, _ = _scenario(session, now)
    PaperTradingService(session, now=now).run()
    match.status, match.home_score, match.away_score = "finished", 2, 0
    session.add(MatchStatistics(match_id=match.id))
    session.commit()
    monkeypatch.setenv("PAPER_ML_RETRAIN_SETTLEMENTS", "999")

    result = PaperTradingService(session, now=now + timedelta(hours=4)).run()
    bet = session.scalar(select(PaperBetRecord))

    assert result["settled"] == 1
    assert bet.status == "won"
    assert bet.profit > 0
    assert result["metrics"]["paper_brier_score"] is not None


def test_same_selection_is_created_only_once_per_day():
    now = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
    session = _session()
    match, first = _scenario(session, now)
    session.add(RecommendationOpportunityRecord(
        match_id=str(match.id), market="under_2_5_goals", selection="Under 2.5",
        bookmaker="paper", offered_odds="2.10",
        metrics={
            "probability": .85, "calibrated_probability": .85,
            "probability_interval": {"low": .83, "high": .89},
            "recommendation_tier": "high_confidence",
        },
        risk="low", score="0.81", safe=True, blocked_reasons=[], explanation=[],
        correlation_key=f"{match.id}:result", evaluated_at=now + timedelta(minutes=5),
    ))
    session.commit()

    result = PaperTradingService(session, now=now + timedelta(minutes=10)).run()

    assert result["created"] == 1
    assert len(session.scalars(select(PaperBetRecord)).all()) == 1


def test_non_high_confidence_is_observed_without_exposure():
    now = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
    session = _session()
    _, opportunity = _scenario(session, now)
    opportunity.metrics = {
        **opportunity.metrics,
        "recommendation_tier": "statistical_value",
    }
    session.commit()

    PaperTradingService(session, now=now).run()
    bet = session.scalar(select(PaperBetRecord))

    assert bet.stake == 0
    assert bet.snapshot["mode"] == "shadow_observation"


def test_pending_stakes_respect_daily_and_match_exposure(monkeypatch):
    now = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
    session = _session()
    match, _ = _scenario(session, now)
    for index in range(1, 5):
        session.add(RecommendationOpportunityRecord(
            match_id=str(match.id), market=f"market_{index}", selection="home",
            bookmaker="paper", offered_odds="2.00",
            metrics={
                "probability": .85, "calibrated_probability": .85,
                "probability_interval": {"low": .82, "high": .89},
                "recommendation_tier": "high_confidence",
            },
            risk="low", score="0.8", safe=True, blocked_reasons=[], explanation=[],
            correlation_key=f"{match.id}:{index}", evaluated_at=now,
        ))
    session.commit()
    monkeypatch.setenv("PAPER_TRADING_MATCH_EXPOSURE", "0.01")

    PaperTradingService(session, now=now).run()
    bets = session.scalars(select(PaperBetRecord)).all()

    assert sum(row.stake for row in bets) <= 100
    assert sum(row.stake for row in bets if row.status == "pending") <= 100


def test_stale_price_is_visible_but_never_receives_stake(monkeypatch):
    now = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
    session = _session()
    _, opportunity = _scenario(session, now)
    opportunity.metrics = {**opportunity.metrics, "odds_age_hours": 1.0}
    session.commit()
    monkeypatch.setenv("PAPER_TRADING_MAX_ODDS_AGE_HOURS", "0.5")

    PaperTradingService(session, now=now).run()
    bet = session.scalar(select(PaperBetRecord))

    assert bet.stake == 0
    assert bet.snapshot["price_is_valid"] is False
    assert bet.snapshot["expires_at"]
    assert bet.snapshot["minimum_valid_odds"] > 1


def test_drawdown_circuit_breaker_stops_new_exposure(monkeypatch):
    now = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
    session = _session()
    _scenario(session, now)
    service = PaperTradingService(session, now=now)
    portfolio = service._portfolio()
    portfolio.current_balance = 8500
    portfolio.peak_balance = 10000
    session.commit()
    monkeypatch.setenv("PAPER_TRADING_MAX_DRAWDOWN", "0.10")

    result = service.run()
    bet = session.scalar(select(PaperBetRecord))

    assert bet.stake == 0
    assert bet.snapshot["circuit_breaker"]["open"] is True
    assert "drawdown_limit" in result["metrics"]["circuit_breaker"]["reasons"]


def test_aggregate_market_and_correlation_caps_are_enforced(monkeypatch):
    now = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
    session = _session()
    match, first = _scenario(session, now)
    for index in range(1, 6):
        session.add(RecommendationOpportunityRecord(
            match_id=str(match.id), market="under_3_5_goals",
            selection=f"Under 3.5 #{index}", bookmaker="paper", offered_odds="2.00",
            metrics={**first.metrics}, risk="low", score="0.8", safe=True,
            blocked_reasons=[], explanation=[],
            correlation_key=f"{match.id}:goals", evaluated_at=now + timedelta(seconds=index),
        ))
    session.commit()
    monkeypatch.setenv("PAPER_TRADING_MATCH_EXPOSURE", "1")
    monkeypatch.setenv("PAPER_TRADING_MARKET_EXPOSURE", "0.006")
    monkeypatch.setenv("PAPER_TRADING_CORRELATION_EXPOSURE", "0.007")

    PaperTradingService(session, now=now + timedelta(minutes=1)).run()
    bets = session.scalars(select(PaperBetRecord)).all()

    assert sum(row.stake for row in bets if row.market == "under_3_5_goals") <= 60
    assert sum(row.stake for row in bets) <= 70


def test_void_and_official_result_correction_recompute_portfolio(monkeypatch):
    now = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
    session = _session()
    match, _ = _scenario(session, now)
    service = PaperTradingService(session, now=now)
    service.run()
    match.status, match.home_score, match.away_score = "finished", 2, 1
    session.add(MatchStatistics(match_id=match.id))
    session.commit()

    PaperTradingService(session, now=now + timedelta(hours=4)).run()
    bet = session.scalar(select(PaperBetRecord))
    assert bet.status == "lost"
    lost_balance = session.scalar(select(PaperPortfolioRecord)).current_balance

    match.home_score, match.away_score = 2, 0
    session.commit()
    result = PaperTradingService(session, now=now + timedelta(hours=5)).run()
    portfolio = session.scalar(select(PaperPortfolioRecord))

    assert result["corrected"] == 1
    assert bet.status == "won"
    assert portfolio.current_balance > lost_balance
    assert bet.snapshot["correction"]["from"] == "lost"


def test_promotion_gate_reports_negative_roi_clv_and_calibration():
    now = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
    session = _session()
    match, opportunity = _scenario(session, now)
    service = PaperTradingService(session, now=now)
    portfolio = service._portfolio()
    session.add(PaperBetRecord(
        portfolio_id=portfolio.id, opportunity_id=opportunity.id,
        match_id=str(match.id), competition_id=str(match.competition_id),
        market="under_2_5_goals", selection="Under 2.5", risk="high",
        offered_odds=2, closing_odds=1.8, probability=.9, stake=10,
        payout=0, profit=-10, clv=-.05, status="lost", snapshot={
            "mode": "paper_executed", "policy": "selective_reserved_exposure_v2"
        }, recommended_at=now, kickoff_at=now + timedelta(hours=2), settled_at=now,
    ))
    session.commit()

    metrics = service.metrics()
    segment = next(iter(metrics["segments"].values()))

    assert segment["eligible_for_policy"] is False
    assert {"insufficient_samples", "non_positive_roi", "negative_or_missing_clv",
            "calibration_degraded"}.issubset(segment["promotion_gate_failures"])
    assert metrics["cohorts"]["selective_reserved_exposure_v2:paper_executed"]["yield"] == -1
