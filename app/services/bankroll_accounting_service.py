from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    BankrollTransaction,
    Bet,
)
from app.repositories import (
    BankrollRepository,
    BankrollTransactionRepository,
)


class BankrollAccountingService:
    """
    Faz os débitos e créditos relacionados
    às apostas.

    Este service não executa commit.
    O commit será controlado pelo service principal.
    """

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

    def reserve_stake(
        self,
        bet: Bet,
    ) -> BankrollTransaction:
        if bet.bankroll_id is None:
            raise ValueError(
                "A aposta não possui banca vinculada."
            )

        if bet.stake_amount is None:
            raise ValueError(
                "A aposta não possui valor monetário."
            )

        existing_transaction = (
            self.transaction_repository
            .find_by_bet_and_type(
                bet_id=bet.id,
                transaction_type="bet_stake",
            )
        )

        if existing_transaction:
            raise ValueError(
                "A stake dessa aposta já foi debitada."
            )

        bankroll = (
            self.bankroll_repository.find_by_id(
                bet.bankroll_id
            )
        )

        if not bankroll:
            raise ValueError(
                "Banca da aposta não encontrada."
            )

        stake_amount = Decimal(
            str(bet.stake_amount)
        )

        balance_before = Decimal(
            str(bankroll.current_balance)
        )

        if stake_amount <= 0:
            raise ValueError(
                "A stake deve ser positiva."
            )

        if balance_before < stake_amount:
            raise ValueError(
                "Saldo insuficiente para a aposta."
            )

        balance_after = (
            balance_before - stake_amount
        )

        bankroll.current_balance = (
            balance_after
        )

        self.bankroll_repository.update(
            bankroll
        )

        transaction = BankrollTransaction(
            bankroll_id=bankroll.id,
            bet_id=bet.id,
            transaction_type="bet_stake",
            amount=-stake_amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=(
                f"Stake da aposta {bet.id}"
            ),
        )

        self.transaction_repository.create(
            transaction
        )

        return transaction

    def settle_bet(
        self,
        bet: Bet,
    ) -> BankrollTransaction | None:
        if bet.bankroll_id is None:
            return None

        if bet.stake_amount is None:
            return None

        existing_transaction = (
            self.transaction_repository
            .find_by_bet_and_type(
                bet_id=bet.id,
                transaction_type=(
                    "bet_settlement"
                ),
            )
        )

        if existing_transaction:
            return existing_transaction

        bankroll = (
            self.bankroll_repository.find_by_id(
                bet.bankroll_id
            )
        )

        if not bankroll:
            raise ValueError(
                "Banca da aposta não encontrada."
            )

        stake_amount = Decimal(
            str(bet.stake_amount)
        )

        odd_value = Decimal(
            str(bet.odd_value)
        )

        if bet.result == "won":
            payout = (
                stake_amount * odd_value
            )

        elif bet.result == "void":
            payout = stake_amount

        elif bet.result == "lost":
            payout = Decimal("0.00")

        else:
            raise ValueError(
                "Resultado da aposta inválido."
            )

        bet.payout_amount = payout

        if payout <= 0:
            return None

        balance_before = Decimal(
            str(bankroll.current_balance)
        )

        balance_after = (
            balance_before + payout
        )

        bankroll.current_balance = (
            balance_after
        )

        self.bankroll_repository.update(
            bankroll
        )

        transaction = BankrollTransaction(
            bankroll_id=bankroll.id,
            bet_id=bet.id,
            transaction_type=(
                "bet_settlement"
            ),
            amount=payout,
            balance_before=balance_before,
            balance_after=balance_after,
            description=(
                f"Liquidação da aposta {bet.id}"
            ),
        )

        self.transaction_repository.create(
            transaction
        )

        return transaction