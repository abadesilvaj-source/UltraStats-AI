from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BankrollTransaction
from datetime import datetime, timedelta

from sqlalchemy import func, select


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
    def find_by_bet_and_type(
        self,
        bet_id: int,
        transaction_type: str,
    ) -> BankrollTransaction | None:
        statement = select(
            BankrollTransaction
        ).where(
            BankrollTransaction.bet_id == bet_id,
            BankrollTransaction.transaction_type
            == transaction_type,
        )

        return self.session.scalar(statement)

    def get_daily_stake_exposure(
        self,
        bankroll_id: int,
        reference_date: datetime | None = None,
    ) -> float:
        """
        Soma todas as stakes debitadas da banca no dia.
        """

        if reference_date is None:
            reference_date = datetime.now()

        start_of_day = reference_date.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        end_of_day = (
            start_of_day
            + timedelta(days=1)
        )

        statement = select(
            func.coalesce(
                func.sum(
                    BankrollTransaction.amount
                ),
                0,
            )
        ).where(
            BankrollTransaction.bankroll_id
            == bankroll_id,
            BankrollTransaction.transaction_type
            == "bet_stake",
            BankrollTransaction.created_at
            >= start_of_day,
            BankrollTransaction.created_at
            < end_of_day,
        )

        value = self.session.scalar(
            statement
        )

        return abs(float(value or 0))
    
    def find_by_id(
        self,
        transaction_id: int,
    ) -> BankrollTransaction | None:
        return self.session.get(
            BankrollTransaction,
            transaction_id,
        )