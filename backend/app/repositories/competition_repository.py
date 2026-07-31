from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Competition


class CompetitionRepository:
    """Operações de banco relacionadas às competições."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def find_by_id(
        self,
        competition_id: int,
    ) -> Competition | None:
        return self.session.get(
            Competition,
            competition_id,
        )

    def find_by_name_and_season(
        self,
        name: str,
        season: str,
    ) -> Competition | None:
        statement = select(
            Competition
        ).where(
            Competition.name == name,
            Competition.season == season,
        )

        return self.session.scalar(
            statement
        )

    def find_by_source_and_external_id(
        self,
        source: str,
        external_id: str,
    ) -> Competition | None:
        statement = select(
            Competition
        ).where(
            Competition.source == source,
            Competition.external_id
            == external_id,
        )

        return self.session.scalar(
            statement
        )

    def create(
        self,
        competition: Competition,
    ) -> Competition:
        self.session.add(
            competition
        )

        self.session.flush()

        return competition

    def update(
        self,
        competition: Competition,
    ) -> Competition:
        self.session.flush()

        return competition