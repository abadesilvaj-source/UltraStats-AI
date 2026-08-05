from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Match
from app.services.player_impact_service import PlayerImpactService
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    FeatureSnapshotRecord,
    RawProviderPayloadRecord,
)


NOW = datetime.now(timezone.utc)


def raw(resource, external_id, payload, *, collected_at=NOW):
    return RawProviderPayloadRecord(
        provider="api_football",
        resource=resource,
        external_id=external_id,
        fingerprint=f"{resource}:{external_id}",
        payload=payload,
        collected_at=collected_at,
    )


def player(player_id, *, rating=7.0, goals=0, assists=0, position="Midfielder"):
    return {
        "player": {"id": player_id, "name": f"Player {player_id}"},
        "statistics": [{
            "games": {"minutes": 90, "rating": str(rating), "position": position},
            "goals": {"total": goals, "assists": assists},
            "shots": {"on": goals + 1},
            "passes": {"key": assists + 1},
            "tackles": {"total": 2, "interceptions": 1},
        }],
    }


def test_player_impact_uses_confirmed_lineup_and_weighted_absence(monkeypatch):
    monkeypatch.setenv("PLAYER_IMPACT_ENABLED", "true")
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    db = Session(engine)
    db.add(raw("fixtures", "100", {
        "teams": {"home": {"id": 10}, "away": {"id": 20}},
    }))
    home_players = [
        player(index, rating=8.2 if index == 1 else 7.1,
               goals=3 if index == 1 else 0)
        for index in range(1, 12)
    ]
    away_players = [player(index, rating=6.7) for index in range(21, 32)]
    db.add(raw("player_statistics", "90:home", {
        "team": {"id": 10}, "players": home_players,
    }))
    db.add(raw("player_statistics", "90:away", {
        "team": {"id": 20}, "players": away_players,
    }))
    for team_id, ids in ((10, range(1, 12)), (20, range(21, 32))):
        db.add(raw("lineups", f"100:{team_id}", {
            "team": {"id": team_id},
            "startXI": [{"player": {"id": value}} for value in ids],
        }))
    db.add(raw("injuries", "100:1", {
        "fixture": {"id": 100}, "team": {"id": 10},
        "player": {"id": 1, "name": "Player 1"},
    }))
    db.commit()

    match = Match(
        id=1, competition_id=1, home_team_id=1, away_team_id=2,
        kickoff_at=(NOW + timedelta(hours=2)).replace(tzinfo=None),
        status="scheduled", source="api_football", external_id="100",
    )
    result = PlayerImpactService(db).context(match, as_of=NOW, persist=True)
    db.commit()

    assert result["enabled"] is True
    assert result["confidence"] == 1.0
    assert result["home_lineup_status"] == "confirmed"
    assert result["away_lineup_status"] == "confirmed"
    assert result["home_strength"] > result["away_strength"]
    assert result["home_absence_impact"] > 0
    assert result["home_key_absences"][0]["player_id"] == "1"
    assert db.scalar(select(FeatureSnapshotRecord)) is not None


def test_player_impact_is_neutral_without_provider_identity():
    engine = create_engine("sqlite://")
    CanonicalBase.metadata.create_all(engine)
    db = Session(engine)
    match = Match(
        id=2, competition_id=1, home_team_id=1, away_team_id=2,
        kickoff_at=(NOW + timedelta(hours=2)).replace(tzinfo=None),
        status="scheduled", source="unknown", external_id=None,
    )
    result = PlayerImpactService(db).context(match, as_of=NOW)
    assert result == PlayerImpactService.neutral()
