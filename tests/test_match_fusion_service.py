from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Competition, Match, Team
from app.services.match_fusion_service import MatchFusionService
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    FusionResultRecord,
    IdentityDecisionRecord,
)
from ultrastats_ai.infrastructure.providers import (
    DataCapability,
    SourceObservation,
)


def database() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    CanonicalBase.metadata.create_all(engine)
    return Session(engine)


def api_observation(kickoff: datetime) -> SourceObservation:
    return SourceObservation(
        "api_football",
        DataCapability.FIXTURES,
        "101",
        {
            "fixture": {
                "id": 101,
                "date": kickoff.isoformat(),
                "status": {"short": "FT"},
                "venue": {"name": "Arena API"},
            },
            "league": {"name": "Liga Teste"},
            "teams": {
                "home": {"name": "São Paulo FC"},
                "away": {"name": "Santos FC"},
            },
            "goals": {"home": 2, "away": 1},
        },
        datetime.now(timezone.utc),
    )


def test_fusion_matches_aliases_and_records_field_provenance():
    session = database()
    kickoff = datetime.now(timezone.utc) - timedelta(hours=2)
    competition = Competition(name="Liga Teste", sport="football")
    home, away = Team(name="Sao Paulo"), Team(name="Santos")
    session.add_all((competition, home, away))
    session.flush()
    match = Match(
        competition_id=competition.id,
        home_team_id=home.id,
        away_team_id=away.id,
        kickoff_at=kickoff,
        status="in_progress",
        external_id="101",
    )
    session.add(match)
    session.flush()
    payload = {
        "matches": [{
            "id": 999,
            "utcDate": kickoff.isoformat(),
            "status": "FINISHED",
            "competition": {"name": "Liga Teste"},
            "homeTeam": {"name": "São Paulo"},
            "awayTeam": {"name": "Santos"},
            "score": {"fullTime": {"home": 2, "away": 1}},
        }]
    }
    result = MatchFusionService(session).fuse(
        (api_observation(kickoff),),
        football_data_payload=payload,
    )
    session.commit()

    assert result["matched"] == 2
    assert session.get(Match, match.id).status == "finished"
    fused = session.scalar(select(FusionResultRecord))
    assert set(fused.provenance["home_score"]["contributors"]) == {
        "api_football", "football_data"
    }
    assert len(session.scalars(select(IdentityDecisionRecord)).all()) == 2


def test_fusion_creates_canonical_match_from_secondary_source():
    session = database()
    kickoff = datetime.now(timezone.utc) + timedelta(days=1)
    result = MatchFusionService(session).fuse(
        (),
        football_data_payload={
            "matches": [{
                "id": 777,
                "utcDate": kickoff.isoformat(),
                "status": "SCHEDULED",
                "competition": {"name": "Nova Liga"},
                "homeTeam": {"name": "Clube A"},
                "awayTeam": {"name": "Clube B"},
                "score": {"fullTime": {"home": None, "away": None}},
            }]
        },
    )
    session.commit()

    assert result["created"] == 1
    match = session.scalar(select(Match))
    assert match.source == "data_fusion"
    assert match.status == "scheduled"


def test_openligadb_adapter_accepts_null_location():
    session = database()
    kickoff = datetime.now(timezone.utc) + timedelta(days=1)
    observation = SourceObservation(
        "openligadb",
        DataCapability.FIXTURES,
        "808",
        {
            "matchID": 808,
            "matchDateTimeUTC": kickoff.isoformat(),
            "matchIsFinished": False,
            "leagueName": "Liga sem estádio",
            "team1": {"teamName": "Clube C"},
            "team2": {"teamName": "Clube D"},
            "matchResults": [],
            "location": None,
        },
        datetime.now(timezone.utc),
    )

    result = MatchFusionService(session).fuse((observation,))
    session.commit()

    assert result["created"] == 1
    match = session.scalar(select(Match))
    assert match.venue is None
