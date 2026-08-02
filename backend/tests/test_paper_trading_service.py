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
        match_id=str(match.id), market="match_winner", selection="home",
        bookmaker="paper", offered_odds="2.00",
        metrics={"probability": .60, "calibrated_probability": .60},
        risk="low", score="0.8", safe=True, blocked_reasons=[], explanation=[],
        correlation_key=f"{match.id}:result", evaluated_at=now,
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
    assert result["metrics"]["brier"] is not None
