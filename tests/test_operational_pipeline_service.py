from datetime import datetime, timezone
from copy import deepcopy

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import (
    Competition,
    Market,
    Match,
    MatchStatistics,
    Odd,
    Prediction,
    Team,
)
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


def external_odds():
    return SourceObservation(
        "the_odds_api",
        DataCapability.ODDS,
        "external-100",
        {
            "id": "external-100",
            "commence_time": "2026-07-24T20:00:00Z",
            "home_team": "Home FC",
            "away_team": "Away FC",
            "bookmakers": [{
                "key": "testbook",
                "title": "Test Book",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Home FC", "price": 2.1},
                            {"name": "Draw", "price": 3.2},
                            {"name": "Away FC", "price": 3.4},
                        ],
                    },
                    {
                        "key": "totals",
                        "outcomes": [
                            {"name": "Over", "point": 2.5, "price": 1.9},
                            {"name": "Under", "point": 2.5, "price": 1.95},
                        ],
                    },
                ],
            }],
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
        "markets": 8,
        "odds": 7,
        "predictions": 11,
    }
    assert db.scalar(select(func.count()).select_from(Competition)) == 1
    assert db.scalar(select(func.count()).select_from(Team)) == 2
    assert db.scalar(select(func.count()).select_from(Match)) == 1
    assert db.scalar(select(func.count()).select_from(Market)) == 8
    assert db.scalar(select(func.count()).select_from(Odd)) == 7
    assert db.scalar(select(func.count()).select_from(Prediction)) == 11
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


def test_pipeline_associates_external_odds_by_teams_and_kickoff():
    db = session()
    service = OperationalPipelineService(db)
    result = service.process(
        fixtures=(fixture(),),
        odds=(external_odds(),),
    )
    db.commit()

    assert result["odds"] == 5
    assert {
        (item.selection, float(item.odd_value))
        for item in db.scalars(select(Odd)).all()
    } >= {
        ("Home", 2.1),
        ("Draw", 3.2),
        ("Away", 3.4),
        ("Over 2.5", 1.9),
        ("Under 2.5", 1.95),
    }


def test_winner_prediction_uses_match_specific_odds_consensus():
    db = session()
    service = OperationalPipelineService(db)
    first_fixture = fixture("100")
    second_fixture = fixture("101")
    second_fixture.values["fixture"]["date"] = "2026-07-24T22:00:00+00:00"
    first_odds = odds()
    second_values = deepcopy(odds().values)
    second_values["fixture"]["id"] = 101
    winner = second_values["bookmakers"][0]["bets"][0]["values"]
    winner[0]["odd"] = "4.50"
    winner[2]["odd"] = "1.65"
    second_odds = SourceObservation(
        "api_football",
        DataCapability.ODDS,
        "101",
        second_values,
        NOW,
    )

    service.process(
        fixtures=(first_fixture, second_fixture),
        odds=(first_odds, second_odds),
    )
    db.commit()
    market_id = db.scalar(
        select(Market.id).where(Market.code == "match_winner")
    )
    first_home = db.scalar(select(Prediction.probability).where(
        Prediction.match_id == 1,
        Prediction.market_id == market_id,
        Prediction.selection == "Home",
    ))
    second_away = db.scalar(select(Prediction.probability).where(
        Prediction.match_id == 2,
        Prediction.market_id == market_id,
        Prediction.selection == "Away",
    ))

    assert second_away > first_home


def test_pipeline_persists_final_statistics_automatically():
    db = session()
    finished = fixture()
    finished.values["fixture"]["status"] = {"short": "FT"}
    finished.values["goals"] = {"home": 2, "away": 1}
    pipeline = OperationalPipelineService(db)
    pipeline.process(fixtures=(finished,))
    statistics = tuple(
        SourceObservation(
            "api_football",
            DataCapability.STATISTICS,
            str(team_id),
            {
                "team": {"id": team_id},
                "statistics": [
                    {"type": "Corner Kicks", "value": corners},
                    {"type": "Yellow Cards", "value": cards},
                    {"type": "Red Cards", "value": 0},
                    {"type": "Total Shots", "value": 12},
                    {"type": "Shots on Goal", "value": 5},
                    {"type": "Offsides", "value": 2},
                    {"type": "Ball Possession", "value": possession},
                    {"type": "expected_goals", "value": xg},
                ],
            },
            NOW,
        )
        for team_id, corners, cards, possession, xg in (
            (1, 6, 2, "55%", "1.70"),
            (2, 3, 4, "45%", "0.80"),
        )
    )
    result = pipeline.process_post_match_statistics(finished, statistics)
    stored = db.scalar(select(MatchStatistics))
    assert result == {"statistics": 1, "settled_bets": 0}
    assert stored.corners_home == 6
    assert stored.yellow_cards_away == 4
    assert stored.offsides_home == 2
    assert stored.possession_home == 55
    assert stored.xg_away == .8
