from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Team


class TeamRepository:
    """Responsável pelas operações de banco relacionadas às equipes."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_name(self, name: str) -> Team | None:
        statement = select(Team).where(Team.name == name)
        return self.session.scalar(statement)

    def list_all(self) -> list[Team]:
        statement = select(Team).order_by(Team.name)
        return list(self.session.scalars(statement).all())

    def create(self, team: Team) -> Team:
        self.session.add(team)
        self.session.commit()
        self.session.refresh(team)

        return team
    
    def find_by_id(
        self,
        team_id: int,
    ) -> Team | None:
        return self.session.get(
            Team,
            team_id,
        )