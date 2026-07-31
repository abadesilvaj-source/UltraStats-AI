from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Team


class TeamRepository:
    """Operações de banco relacionadas às equipes."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def find_by_id(
        self,
        team_id: int,
    ) -> Team | None:
        return self.session.get(
            Team,
            team_id,
        )

    def find_by_name(
        self,
        name: str,
    ) -> Team | None:
        statement = select(
            Team
        ).where(
            Team.name == name
        )

        return self.session.scalar(
            statement
        )

    def find_by_source_and_external_id(
        self,
        source: str,
        external_id: str,
    ) -> Team | None:
        statement = select(
            Team
        ).where(
            Team.source == source,
            Team.external_id == external_id,
        )

        return self.session.scalar(
            statement
        )

    def list_all(
        self,
    ) -> list[Team]:
        statement = select(
            Team
        ).order_by(
            Team.name
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def create(
        self,
        team: Team,
    ) -> Team:
        self.session.add(
            team
        )

        self.session.flush()

        return team

    def update(
        self,
        team: Team,
    ) -> Team:
        self.session.flush()

        return team