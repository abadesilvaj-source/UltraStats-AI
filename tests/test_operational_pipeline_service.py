from datetime import datetime, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Competition, Market, Match, Odd, Prediction, Team
from app.services.operational_pipeline_service import OperationalPipelineService
from ultrastats_ai.infrastructure.providers import (
    DataCapability,
    SourceObservation,
)


NOW = datetime.now(timezone.utc)


def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return Session(engine)


def fixture(external_id="100"):
    return SourceObservation(
        "api_football",
        DataCapability.FIXTURES,
        external_id,
        {
            "fixture": {
                "id": int(external_id),
                "date": "2026-07-24T20:00:00+00:00",
                "status": {"short": "NS"},
                "venue": {"name": "Arena"},
            },
            "league": {
                "id": 10,
                "name": "Test League",
                "country": "Brazil",
                "season": 2026,
            },
            "teams": {
                "home": {"id": 1, "name": "Home FC"},
                "away": {"id": 2, "name": "Away FC"},
            },
            "goals": {"home": None, "away": None},
        },
        NOW,
    )


def odds():
    return SourceObservation(
        "api_football",
        DataCapability.ODDS,
        "100",
        {
            "fixture": {"id": 100},
            "bookmakers": [
                {
                    "name": "Book",
                    "bets": [
                        {
                            "name": "Match Winner",
                            "values": [
                                {"value": "Home", "odd": "2.10"},
                                {"value": "Draw", "odd": "3.20"},
                                {"value": "Away", "odd": "3.40"},
                            ],
                        },
                        {
                            "name": "Goals Over/Under",
                            "values": [
                                {"value": "Over 2.5", "odd": "1.90"},
                                {"value": "Under 2.5", "odd": "1.95"},
                            ],
                        },
                        {
                            "name": "Both Teams Score",
                            "values": [
                                {"value": "Yes", "odd": "1.80"},
                                {"value": "No", "odd": "2.00"},
                            ],
                        },
                    ],
                }
            ],
        },
        NOW,
    )


def test_pipeline_promotes_fixture_odds_markets_and_predictions():
    db = session()
    service = OperationalPipelineService(db)
    result = service.process(fixtures=(fixture(),), odds=(odds(),))
    db.commit()
    assert result == {
        "competitions": 1,
        "teams": 2,
        "matches": 1,
        "markets": 4,
        "odds": 7,
        "predictions": 7,
    }
    assert db.scalar(select(func.count()).select_from(Competition)) == 1
    assert db.scalar(select(func.count()).select_from(Team)) == 2
    assert db.scalar(select(func.count()).select_from(Match)) == 1
    assert db.scalar(select(func.count()).select_from(Market)) == 4
    assert db.scalar(select(func.count()).select_from(Odd)) == 7
    assert db.scalar(select(func.count()).select_from(Prediction)) == 7
    prediction = db.scalar(
        select(Prediction).where(Prediction.selection == "Home")
    )
    assert prediction.implied_probability is not None
    assert prediction.expected_value is not None


def test_pipeline_is_idempotent_and_ignores_non_api_fixtures():
    db = session()
    service = OperationalPipelineService(db)
    first = service.process(fixtures=(fixture(),), odds=(odds(),))
    db.commit()
    second = service.process(
        fixtures=(
            fixture(),
            SourceObservation(
                "openligadb",
                DataCapability.FIXTURES,
                "x",
                {},
                NOW,
            ),
        ),
        odds=(odds(),),
    )
    db.commit()
    assert first["matches"] == 1
    assert second["matches"] == 0
    assert second["odds"] == 0
    assert second["predictions"] == 0
