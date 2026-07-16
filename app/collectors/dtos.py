from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CompetitionDTO:
    source: str
    external_id: str
    name: str
    country: str | None
    season: str | None
    sport: str = "football"


@dataclass(frozen=True)
class TeamDTO:
    source: str
    external_id: str
    name: str
    country: str | None
    league: str | None


@dataclass(frozen=True)
class MatchDTO:
    source: str
    external_id: str

    competition_external_id: str
    home_team_external_id: str
    away_team_external_id: str

    kickoff_at: datetime
    status: str

    home_score: int | None = None
    away_score: int | None = None
    venue: str | None = None