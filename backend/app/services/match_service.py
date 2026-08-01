from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Match
from app.repositories import (
    CompetitionRepository,
    MatchRepository,
    TeamRepository,
)


class MatchService:
    """Aplica as regras de negócio relacionadas às partidas."""

    def __init__(self, session: Session) -> None:
        self.match_repository = MatchRepository(session)
        self.team_repository = TeamRepository(session)
        self.competition_repository = CompetitionRepository(session)

    def create_match(
        self,
        competition_name: str,
        competition_season: str,
        home_team_name: str,
        away_team_name: str,
        kickoff_at: datetime,
        venue: str,
        source: str,
        external_id: str,
    ) -> Match:
        existing_match = self.match_repository.find_by_external_id(
            external_id
        )

        if existing_match:
            raise ValueError(
                "Essa partida já está cadastrada."
            )

        competition = (
            self.competition_repository.find_by_name_and_season(
                competition_name,
                competition_season,
            )
        )

        if not competition:
            raise ValueError(
                "Competição não encontrada."
            )

        home_team = self.team_repository.find_by_name(
            home_team_name
        )

        away_team = self.team_repository.find_by_name(
            away_team_name
        )

        if not home_team:
            raise ValueError(
                f"Equipe mandante '{home_team_name}' não encontrada."
            )

        if not away_team:
            raise ValueError(
                f"Equipe visitante '{away_team_name}' não encontrada."
            )

        if home_team.id == away_team.id:
            raise ValueError(
                "Mandante e visitante não podem ser a mesma equipe."
            )

        match = Match(
            competition_id=competition.id,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            kickoff_at=kickoff_at,
            status="scheduled",
            venue=venue,
            source=source,
            external_id=external_id,
        )

        return self.match_repository.create(match)

    def list_matches(self) -> list[Match]:
        return self.match_repository.list_all()