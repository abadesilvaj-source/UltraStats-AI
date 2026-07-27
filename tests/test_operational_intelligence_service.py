from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Competition, Market, Match, Odd, Prediction, Team
from app.services.operational_intelligence_service import (
    OperationalIntelligenceService,
)
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    ModelBacktestRecord,
    ModelValidationRecord,
    PredictiveModelRecord,
    RecommendationOpportunityRecord,
    TrainingDatasetRecord,
)


def test_materializes_model_lifecycle_and_recommendations():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    CanonicalBase.metadata.create_all(engine)
    session = Session(engine)
    competition = Competition(name="Liga ML", sport="football")
    home, away = Team(name="Casa ML"), Team(name="Fora ML")
    market = Market(
        code="match_winner",
        name="Resultado",
        category="result",
    )
    session.add_all((competition, home, away, market))
    session.flush()
    match = Match(
        competition_id=competition.id,
        home_team_id=home.id,
        away_team_id=away.id,
        kickoff_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status="scheduled",
        external_id="ml-1",
    )
    session.add(match)
    session.flush()
    prediction = Prediction(
        match_id=match.id,
        market_id=market.id,
        selection="Home",
        model_version="operational-poisson-v1",
        probability=.6,
        implied_probability=.5,
        expected_value=.2,
        confidence=.6,
        evidence_level="low",
        risk_level="high",
    )
    session.add(prediction)
    session.add(
        Odd(
            match_id=match.id,
            market_id=market.id,
            bookmaker="Book",
            selection="Home",
            odd_value=2,
        )
    )
    session.flush()

    result = OperationalIntelligenceService(session).run()
    session.commit()

    assert result["recommendations_persisted"] == 1
    assert result["model_approved"] is False
    assert session.scalar(
        select(func.count()).select_from(PredictiveModelRecord)
    ) == 1
    assert session.scalar(
        select(func.count()).select_from(TrainingDatasetRecord)
    ) == 1
    assert session.scalar(
        select(func.count()).select_from(ModelBacktestRecord)
    ) == 1
    assert session.scalar(
        select(func.count()).select_from(ModelValidationRecord)
    ) == 1
    opportunity = session.scalar(
        select(RecommendationOpportunityRecord)
    )
    assert opportunity.safe
    assert opportunity.blocked_reasons == []
    assert opportunity.metrics["warnings"] == ["low_evidence"]
