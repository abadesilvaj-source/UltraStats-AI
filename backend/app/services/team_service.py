from sqlalchemy.orm import Session

from app.models import Team
from app.repositories import TeamRepository


class TeamService:
    """Aplica as regras de negócio relacionadas às equipes."""

    def __init__(self, session: Session) -> None:
        self.repository = TeamRepository(session)

    def create_team(
        self,
        name: str,
        country: str,
        league: str,
        power_rating: float = 50.0,
        attack_rating: float = 50.0,
        defense_rating: float = 50.0,
        corner_rating: float = 50.0,
        card_rating: float = 50.0,
        goal_rating: float = 50.0,
        offside_rating: float = 50.0,
    ) -> Team:
        existing_team = self.repository.find_by_name(name)

        if existing_team:
            raise ValueError(
                f"A equipe '{name}' já está cadastrada."
            )

        team = Team(
            name=name,
            country=country,
            league=league,
            power_rating=power_rating,
            attack_rating=attack_rating,
            defense_rating=defense_rating,
            corner_rating=corner_rating,
            card_rating=card_rating,
            goal_rating=goal_rating,
            offside_rating=offside_rating,
        )

        return self.repository.create(team)

    def list_teams(self) -> list[Team]:
        return self.repository.list_all()