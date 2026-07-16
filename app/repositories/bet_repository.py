from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Bet


class BetRepository:
    """Operações de banco relacionadas às apostas."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, bet: Bet) -> Bet:
        self.session.add(bet)
        self.session.flush()

        return bet

    def find_by_id(
        self,
        bet_id: int,
    ) -> Bet | None:
        return self.session.get(Bet, bet_id)

    def list_all(self) -> list[Bet]:
        statement = select(Bet).order_by(
            Bet.placed_at.desc()
        )

        return list(
            self.session.scalars(statement).all()
        )

    def list_pending_by_match_id(
        self,
        match_id: int,
    ) -> list[Bet]:
        statement = select(Bet).where(
            Bet.match_id == match_id,
            Bet.status == "pending",
        )

        return list(
            self.session.scalars(statement).all()
        )

    def update(self, bet: Bet) -> Bet:
        self.session.flush()

        return bet