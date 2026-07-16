from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    Bankroll,
    BankrollTransaction,
)
from app.repositories import (
    BankrollRepository,
    BankrollTransactionRepository,
)


class BankrollService:
    """Gerencia bancas e movimentações financeiras."""

    def __init__(self, session: Session) -> None:
        self.session = session

        self.bankroll_repository = (
            BankrollRepository(session)
        )

        self.transaction_repository = (
            BankrollTransactionRepository(
                session
            )
        )

    def create_bankroll(
        self,
        name: str,
        initial_balance: float,
        currency: str = "BRL",
        unit_percentage: float = 1.0,
    ) -> Bankroll:
        if initial_balance <= 0:
            raise ValueError(
                "O saldo inicial deve ser maior que zero."
            )

        if unit_percentage <= 0:
            raise ValueError(
                "O percentual da unidade deve ser maior que zero."
            )

        if unit_percentage > 100:
            raise ValueError(
                "O percentual da unidade não pode ultrapassar 100%."
            )

        existing_bankroll = (
            self.bankroll_repository.find_by_name(
                name
            )
        )

        if existing_bankroll:
            raise ValueError(
                f"A banca '{name}' já existe."
            )

        balance = Decimal(
            str(initial_balance)
        )

        try:
            bankroll = Bankroll(
                name=name,
                currency=currency.upper(),
                initial_balance=balance,
                current_balance=balance,
                unit_percentage=unit_percentage,
                active=True,
            )

            self.bankroll_repository.create(
                bankroll
            )

            transaction = BankrollTransaction(
                bankroll_id=bankroll.id,
                bet_id=None,
                transaction_type=(
                    "initial_deposit"
                ),
                amount=balance,
                balance_before=Decimal("0.00"),
                balance_after=balance,
                description=(
                    "Criação da banca"
                ),
            )

            self.transaction_repository.create(
                transaction
            )

            self.session.commit()
            self.session.refresh(bankroll)

            return bankroll

        except Exception:
            self.session.rollback()
            raise

    def get_bankroll(
        self,
        bankroll_id: int,
    ) -> Bankroll:
        bankroll = (
            self.bankroll_repository.find_by_id(
                bankroll_id
            )
        )

        if not bankroll:
            raise ValueError(
                "Banca não encontrada."
            )

        return bankroll

    def list_bankrolls(
        self,
    ) -> list[Bankroll]:
        return self.bankroll_repository.list_all()

    def calculate_unit_value(
        self,
        bankroll_id: int,
    ) -> float:
        bankroll = self.get_bankroll(
            bankroll_id
        )

        current_balance = float(
            bankroll.current_balance
        )

        return (
            current_balance
            * bankroll.unit_percentage
            / 100
        )