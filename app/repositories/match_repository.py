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
   
    def find_by_id(
        self,
        match_id: int,
    ) -> Match | None:
        return self.session.get(Match, match_id)

    def update(self, match: Match) -> Match:
        self.session.flush()

        return match

    def list_available_for_betting(
        self,
    ) -> list[Match]:
        """
        Lista partidas que ainda podem receber apostas.
        """

        statement = (
            select(Match)
            .where(
                Match.status.in_(
                    [
                        "scheduled",
                        "not_started",
                    ]
                )
            )
            .order_by(
                Match.kickoff_at
            )
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )
    
    def list_for_settlement(
        self,
    ) -> list[Match]:
        """
        Lista partidas que podem receber
        resultado administrativo.
        """

        statement = (
            select(Match)
            .where(
                Match.status.in_(
                    [
                        "scheduled",
                        "not_started",
                        "in_progress",
                    ]
                )
            )
            .order_by(
                Match.kickoff_at.desc()
            )
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )