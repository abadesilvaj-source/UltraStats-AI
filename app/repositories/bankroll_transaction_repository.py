from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BankrollTransaction


class BankrollTransactionRepository:
    """Operações de banco relacionadas às movimentações da banca."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        transaction: BankrollTransaction,
    ) -> BankrollTransaction:
        self.session.add(transaction)
        self.session.flush()

        return transaction

    def list_by_bankroll_id(
        self,
        bankroll_id: int,
    ) -> list[BankrollTransaction]:
        statement = (
            select(BankrollTransaction)
            .where(
                BankrollTransaction.bankroll_id
                == bankroll_id
            )
            .order_by(
                BankrollTransaction.created_at,
                BankrollTransaction.id,
            )
        )

        return list(
            self.session.scalars(statement).all()
        )