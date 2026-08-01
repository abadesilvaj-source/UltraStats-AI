from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Bankroll


class BankrollRepository:
    """Operações de banco relacionadas às bancas."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        bankroll: Bankroll,
    ) -> Bankroll:
        self.session.add(bankroll)
        self.session.flush()

        return bankroll

    def find_by_id(
        self,
        bankroll_id: int,
    ) -> Bankroll | None:
        return self.session.get(
            Bankroll,
            bankroll_id,
        )

    def find_by_name(
        self,
        name: str,
        user_id: str | None = None,
    ) -> Bankroll | None:
        statement = select(
            Bankroll
        ).where(
            Bankroll.name == name,
            *([Bankroll.user_id == user_id] if user_id else []),
        )

        return self.session.scalar(statement)

    def list_all(self, user_id: str | None = None) -> list[Bankroll]:
        statement = select(
            Bankroll
        ).where(
            *([Bankroll.user_id == user_id] if user_id else []),
        ).order_by(
            Bankroll.name
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def list_active(
        self,
    ) -> list[Bankroll]:
        statement = (
            select(Bankroll)
            .where(
                Bankroll.active.is_(True)
            )
            .order_by(
                Bankroll.name
            )
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def update(
        self,
        bankroll: Bankroll,
    ) -> Bankroll:
        self.session.flush()

        return bankroll
