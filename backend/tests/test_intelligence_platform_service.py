from datetime import datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Audit, Competition, Market, Match, Prediction, Team
from app.services.intelligence_platform_service import (
    IntelligencePlatformService,
    PersistentTaskQueue,
    market_family,
)
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    FeatureSnapshotRecord,
    ModelDeploymentRecord,
    ProcessingTaskRecord,
)


def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    CanonicalBase.metadata.create_all(engine)
    return Session(engine)


def test_market_families_are_specialized() -> None:
    assert market_family("match_winner") == "results"
    assert market_family("over_2_5_goals") == "goals"
    assert market_family("over_9_5_corners") == "corners"
    assert market_family("over_4_5_cards") == "cards"
    assert market_family("player_shots") == "players"


def test_decision_policy_dimensions_and_selective_threshold() -> None:
    assert IntelligencePlatformService._odds_band(1.45) == "1.01-1.49"
    assert IntelligencePlatformService._odds_band(2.25) == "2.00-2.99"
    assert IntelligencePlatformService._horizon(1) == "post_lineup"
    assert IntelligencePlatformService._horizon(30) == "early"
    samples = []
    for index in range(30):
        probability = .92 if index < 24 else .55
        result = "won" if index < 22 else "lost"
        samples.append((
            Audit(result_status=result, predicted_probability=probability),
            Prediction(probability=probability),
        ))
    threshold, accuracy, coverage = (
        IntelligencePlatformService._selective_threshold(samples)
    )
    assert threshold >= .50
    assert accuracy is not None and accuracy >= .85
    assert 0 < coverage <= 1


def test_persistent_queue_is_idempotent() -> None:
    db = session()
    queue = PersistentTaskQueue(db)
    first = queue.enqueue("prediction", "match:1:v1", {"match_id": 1})
    db.flush()
    second = queue.enqueue("prediction", "match:1:v1", {"match_id": 1})
    assert first.id == second.id
    queue.complete(first)
    db.commit()
    stored = db.scalar(select(ProcessingTaskRecord))
    assert stored.status == "completed"


def test_platform_creates_temporal_features_and_model_portfolio() -> None:
    db = session()
    competition = Competition(
        name="Brazil Série A", country="Brazil", sport="football",
        source="test", external_id="1",
    )
    home = Team(name="Home", source="test", external_id="h")
    away = Team(name="Away", source="test", external_id="a")
    market = Market(code="match_winner", name="Resultado", category="results")
    db.add_all((competition, home, away, market))
    db.flush()
    match = Match(
        competition_id=competition.id,
        home_team_id=home.id,
        away_team_id=away.id,
        kickoff_at=datetime.now() + timedelta(days=1),
        status="scheduled",
        source="test",
        external_id="m1",
    )
    db.add(match)
    db.flush()
    db.add(Prediction(
        match_id=match.id,
        market_id=market.id,
        selection="Home",
        model_version="operational-poisson-v1",
        probability=.55,
        confidence=.6,
        evidence_level="medium",
        risk_level="moderate",
    ))
    db.commit()

    result = IntelligencePlatformService(db).run()
    db.commit()

    assert result["feature_snapshots_created"] == 1
    assert db.scalar(select(FeatureSnapshotRecord)) is not None
    assert len(db.scalars(select(ModelDeploymentRecord)).all()) == 12
