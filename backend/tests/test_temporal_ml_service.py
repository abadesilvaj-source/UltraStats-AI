from collections import deque
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Competition, Match, MatchStatistics, Team
from app.services.temporal_ml_service import TemporalMLService
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase, PredictiveModelRecord,
)


def test_feature_vector_normalizes_mixed_timezone_history():
    def history(last_at):
        return deque([
            {
                "at": last_at,
                "gf": 1.0,
                "ga": 1.0,
                "points": 1.0,
                "xgf": 1.0,
                "xga": 1.0,
                "sot": 3.0,
                "corners": 5.0,
                "cards": 2.0,
            }
        ])

    kickoff = datetime(2026, 8, 2, 15, tzinfo=timezone(timedelta(hours=-3)))
    features = TemporalMLService._feature_vector(
        history(datetime(2026, 8, 1, 18)),
        history(datetime(2026, 8, 1, 15, tzinfo=timezone(timedelta(hours=-3)))),
        kickoff,
    )

    assert features[8] == 0.0


def test_low_latency_worker_does_not_train_when_model_is_missing(monkeypatch):
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    session = Session(engine)
    service = TemporalMLService(session, allow_training=False)
    monkeypatch.setattr(
        service,
        "_dataset",
        lambda: (_ for _ in ()).throw(AssertionError("training was started")),
    )

    assert service._load_or_train() == {}


def test_temporal_model_trains_calibrates_and_predicts_with_strict_history():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    CanonicalBase.metadata.create_all(engine)
    session = Session(engine)
    competition = Competition(name="Premier League", country="England")
    teams = [Team(name=f"Team {index}") for index in range(12)]
    session.add_all((competition, *teams))
    session.flush()
    start = datetime(2022, 1, 1)
    for index in range(420):
        mode = index % 3
        strong = teams[index % 6]
        weak = teams[6 + (index * 5) % 6]
        if mode == 0:
            home, away, score = strong, weak, (3, 0)
        elif mode == 1:
            home, away, score = weak, strong, (0, 2)
        else:
            home = teams[index % 6]
            away = teams[(index + 1) % 6]
            score = (1, 1)
        match = Match(
            competition_id=competition.id,
            home_team_id=home.id,
            away_team_id=away.id,
            kickoff_at=start + timedelta(days=index),
            status="finished",
            home_score=score[0], away_score=score[1],
        )
        session.add(match)
        session.flush()
        session.add(MatchStatistics(
            match_id=match.id,
            shots_on_target_home=score[0] * 2 + 2,
            shots_on_target_away=score[1] * 2 + 2,
            corners_home=6 if score[0] > score[1] else 4,
            corners_away=6 if score[1] > score[0] else 4,
            yellow_cards_home=2, yellow_cards_away=2,
            red_cards_home=0, red_cards_away=0,
            xg_home=score[0] + .2, xg_away=score[1] + .2,
        ))
    upcoming = Match(
        competition_id=competition.id,
        home_team_id=teams[0].id,
        away_team_id=teams[6].id,
        kickoff_at=start + timedelta(days=430),
        status="scheduled",
    )
    session.add(upcoming)
    session.flush()

    predictions = TemporalMLService(session).predict(upcoming)

    assert "match_winner" in predictions
    assert abs(sum(predictions["match_winner"].values()) - 1) < 1e-9
    assert predictions["match_winner"]["Home"] > predictions["match_winner"]["Away"]
    models = session.scalars(select(PredictiveModelRecord).where(
        PredictiveModelRecord.name == "temporal_logistic"
    )).all()
    assert len(models) == 3
    assert all(row.parameters["validation"] == "chronological_70_15_15" for row in models)
    assert all(row.parameters["calibration"] == "temperature_on_holdout" for row in models)
