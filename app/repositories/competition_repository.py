from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Competition


class CompetitionRepository:
    """Responsável pelas operações de banco relacionadas às competições."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_name_and_season(
        self,
        name: str,
        season: str,
    ) -> Competition | None:
        statement = select(Competition).where(
            Competition.name == name,
            Competition.season == season,
        )

        return self.session.scalar(statement)

    def create(
        self,
        competition: Competition,
    ) -> Competition:
        self.session.add(competition)
        self.session.commit()
        self.session.refresh(competition)

        return competition