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

from datetime import datetime

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
        name = name.strip()
        if not name:
            raise ValueError(
                "O nome da banca é obrigatório."
            )

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
    
    def deposit(
        self,
        bankroll_id: int,
        amount: float,
        description: str | None = None,
    ) -> BankrollTransaction:
        """
        Adiciona dinheiro à banca.
        """

        if amount <= 0:
            raise ValueError(
                "O valor do depósito deve ser maior que zero."
            )

        bankroll = self.get_bankroll(
            bankroll_id
        )

        if not bankroll.active:
            raise ValueError(
                "Não é possível movimentar uma banca inativa."
            )

        deposit_amount = Decimal(
            str(amount)
        )

        try:
            balance_before = Decimal(
                str(bankroll.current_balance)
            )

            balance_after = (
                balance_before
                + deposit_amount
            )

            bankroll.current_balance = (
                balance_after
            )

            bankroll.updated_at = datetime.now()

            self.bankroll_repository.update(
                bankroll
            )

            transaction = BankrollTransaction(
                bankroll_id=bankroll.id,
                bet_id=None,
                transaction_type="deposit",
                amount=deposit_amount,
                balance_before=balance_before,
                balance_after=balance_after,
                description=(
                    description
                    or "Depósito manual"
                ),
            )

            self.transaction_repository.create(
                transaction
            )

            self.session.commit()

            self.session.refresh(bankroll)
            self.session.refresh(transaction)

            return transaction

        except Exception:
            self.session.rollback()
            raise

    def withdraw(
        self,
        bankroll_id: int,
        amount: float,
        description: str | None = None,
    ) -> BankrollTransaction:
        """
        Retira dinheiro da banca.
        """

        if amount <= 0:
            raise ValueError(
                "O valor da retirada deve ser maior que zero."
            )

        bankroll = self.get_bankroll(
            bankroll_id
        )

        if not bankroll.active:
            raise ValueError(
                "Não é possível movimentar uma banca inativa."
            )

        withdrawal_amount = Decimal(
            str(amount)
        )

        try:
            balance_before = Decimal(
                str(bankroll.current_balance)
            )

            if withdrawal_amount > balance_before:
                raise ValueError(
                    "Saldo insuficiente para realizar a retirada."
                )

            balance_after = (
                balance_before
                - withdrawal_amount
            )

            bankroll.current_balance = (
                balance_after
            )

            bankroll.updated_at = datetime.now()

            self.bankroll_repository.update(
                bankroll
            )

            transaction = BankrollTransaction(
                bankroll_id=bankroll.id,
                bet_id=None,
                transaction_type="withdrawal",
                amount=-withdrawal_amount,
                balance_before=balance_before,
                balance_after=balance_after,
                description=(
                    description
                    or "Retirada manual"
                ),
            )

            self.transaction_repository.create(
                transaction
            )

            self.session.commit()

            self.session.refresh(bankroll)
            self.session.refresh(transaction)

            return transaction

        except Exception:
            self.session.rollback()
            raise

    def manual_adjustment(
        self,
        bankroll_id: int,
        amount: float,
        description: str,
    ) -> BankrollTransaction:
        """
        Faz um ajuste administrativo na banca.

        Valor positivo aumenta o saldo.
        Valor negativo reduz o saldo.
        """

        if amount == 0:
            raise ValueError(
                "O ajuste não pode ser igual a zero."
            )

        if not description.strip():
            raise ValueError(
                "A descrição do ajuste é obrigatória."
            )

        bankroll = self.get_bankroll(
            bankroll_id
        )

        adjustment_amount = Decimal(
            str(amount)
        )

        try:
            balance_before = Decimal(
                str(bankroll.current_balance)
            )

            balance_after = (
                balance_before
                + adjustment_amount
            )

            if balance_after < 0:
                raise ValueError(
                    "O ajuste deixaria a banca com saldo negativo."
                )

            bankroll.current_balance = (
                balance_after
            )

            bankroll.updated_at = datetime.now()

            self.bankroll_repository.update(
                bankroll
            )

            transaction = BankrollTransaction(
                bankroll_id=bankroll.id,
                bet_id=None,
                transaction_type=(
                    "manual_adjustment"
                ),
                amount=adjustment_amount,
                balance_before=balance_before,
                balance_after=balance_after,
                description=description.strip(),
            )

            self.transaction_repository.create(
                transaction
            )

            self.session.commit()

            self.session.refresh(bankroll)
            self.session.refresh(transaction)

            return transaction

        except Exception:
            self.session.rollback()
            raise

    def set_active_status(
        self,
        bankroll_id: int,
        active: bool,
    ) -> Bankroll:
        """
        Ativa ou desativa uma banca.
        """

        bankroll = self.get_bankroll(
            bankroll_id
        )

        bankroll.active = active
        bankroll.updated_at = datetime.now()

        try:
            self.bankroll_repository.update(
                bankroll
            )

            self.session.commit()
            self.session.refresh(bankroll)

            return bankroll

        except Exception:
            self.session.rollback()
            raise
