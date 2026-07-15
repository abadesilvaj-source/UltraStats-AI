from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Match


class MatchRepository:
    """Responsável pelas operações de banco relacionadas às partidas."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_external_id(
        self,
        external_id: str,
    ) -> Match | None:
        statement = select(Match).where(
            Match.external_id == external_id
        )

        return self.session.scalar(statement)

    def list_all(self) -> list[Match]:
        statement = select(Match).order_by(Match.kickoff_at)

        return list(
            self.session.scalars(statement).all()
        )

    def create(self, match: Match) -> Match:
        self.session.add(match)
        self.session.commit()
        self.session.refresh(match)

        return match