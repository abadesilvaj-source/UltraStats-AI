"""Aggregate Root Bankroll, apostas e liquidações auditáveis."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal

from ultrastats_ai.domain.shared import (
    BankrollAccountId,
    BankrollTransactionId,
    BetId,
    BetLegId,
    BettingMarketId,
    BettingSelectionId,
    BetStatus,
    BookmakerId,
    DomainEnum,
    Money,
    Odds,
    SettlementId,
    UtcTimestamp,
)
from ultrastats_ai.domain.shared.errors import DomainError


class TransactionType(DomainEnum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    BET_STAKE = "bet_stake"
    BET_RETURN = "bet_return"
    ADJUSTMENT_CREDIT = "adjustment_credit"
    ADJUSTMENT_DEBIT = "adjustment_debit"


class SettlementResult(DomainEnum):
    WON = "won"
    LOST = "lost"
    VOID = "void"
    HALF_WON = "half_won"
    HALF_LOST = "half_lost"
    CASH_OUT = "cash_out"


class BankrollDomainError(DomainError):
    """Erro-base do Bankroll Context."""


class InvalidBankrollOperationError(BankrollDomainError):
    """Indica uma operação financeira inconsistente."""


_CREDITS = frozenset(
    {
        TransactionType.DEPOSIT,
        TransactionType.BET_RETURN,
        TransactionType.ADJUSTMENT_CREDIT,
    }
)


@dataclass(frozen=True, slots=True)
class BankrollTransaction:
    id: BankrollTransactionId
    bankroll_id: BankrollAccountId
    transaction_type: TransactionType
    amount: Money
    occurred_at: UtcTimestamp
    description: str
    bet_id: BetId | None = None

    def __post_init__(self) -> None:
        _types(
            (self.id, BankrollTransactionId, "id"),
            (self.bankroll_id, BankrollAccountId, "bankroll_id"),
            (self.transaction_type, TransactionType, "transaction_type"),
            (self.amount, Money, "amount"),
            (self.occurred_at, UtcTimestamp, "occurred_at"),
            (self.description, str, "description"),
        )
        if self.bet_id is not None:
            _types((self.bet_id, BetId, "bet_id"))
        if self.amount.amount <= 0 or not self.description.strip():
            raise InvalidBankrollOperationError(
                "Transação exige valor positivo e descrição."
            )

    @property
    def signed_amount(self) -> Decimal:
        if self.transaction_type in _CREDITS:
            return self.amount.amount
        return -self.amount.amount


@dataclass(frozen=True, slots=True)
class BetLeg:
    id: BetLegId
    bet_id: BetId
    market_id: BettingMarketId
    selection_id: BettingSelectionId
    odds: Odds
    status: BetStatus = BetStatus.PENDING

    def __post_init__(self) -> None:
        _types(
            (self.id, BetLegId, "id"),
            (self.bet_id, BetId, "bet_id"),
            (self.market_id, BettingMarketId, "market_id"),
            (self.selection_id, BettingSelectionId, "selection_id"),
            (self.odds, Odds, "odds"),
            (self.status, BetStatus, "status"),
        )


@dataclass(frozen=True, slots=True)
class Bet:
    id: BetId
    bankroll_id: BankrollAccountId
    bookmaker_id: BookmakerId
    stake: Money
    odds: Odds
    status: BetStatus
    placed_at: UtcTimestamp
    legs: tuple[BetLeg, ...]

    def __post_init__(self) -> None:
        _types(
            (self.id, BetId, "id"),
            (self.bankroll_id, BankrollAccountId, "bankroll_id"),
            (self.bookmaker_id, BookmakerId, "bookmaker_id"),
            (self.stake, Money, "stake"),
            (self.odds, Odds, "odds"),
            (self.status, BetStatus, "status"),
            (self.placed_at, UtcTimestamp, "placed_at"),
            (self.legs, tuple, "legs"),
        )
        if self.stake.amount <= 0 or not self.legs:
            raise InvalidBankrollOperationError(
                "Aposta exige stake positiva e pernas."
            )
        ids: set[BetLegId] = set()
        combined = Decimal("1")
        for leg in self.legs:
            _types((leg, BetLeg, "leg"))
            if leg.bet_id != self.id or leg.id in ids:
                raise InvalidBankrollOperationError(
                    "Perna inválida ou duplicada."
                )
            ids.add(leg.id)
            combined *= leg.odds.value
        if abs(combined - self.odds.value) > Decimal("0.0001"):
            raise InvalidBankrollOperationError(
                "Odd combinada diverge das pernas."
            )


@dataclass(frozen=True, slots=True)
class Settlement:
    id: SettlementId
    bankroll_id: BankrollAccountId
    bet_id: BetId
    result: SettlementResult
    return_amount: Money
    settled_at: UtcTimestamp
    rule: str

    def __post_init__(self) -> None:
        _types(
            (self.id, SettlementId, "id"),
            (self.bankroll_id, BankrollAccountId, "bankroll_id"),
            (self.bet_id, BetId, "bet_id"),
            (self.result, SettlementResult, "result"),
            (self.return_amount, Money, "return_amount"),
            (self.settled_at, UtcTimestamp, "settled_at"),
            (self.rule, str, "rule"),
        )
        if self.return_amount.amount < 0 or not self.rule.strip():
            raise InvalidBankrollOperationError(
                "Liquidação exige retorno não negativo e regra."
            )


@dataclass(frozen=True, slots=True)
class Bankroll:
    id: BankrollAccountId
    name: str
    currency: str
    initial_balance: Money
    transactions: tuple[BankrollTransaction, ...] = ()
    bets: tuple[Bet, ...] = ()
    settlements: tuple[Settlement, ...] = ()

    def __post_init__(self) -> None:
        _types(
            (self.id, BankrollAccountId, "id"),
            (self.name, str, "name"),
            (self.currency, str, "currency"),
            (self.initial_balance, Money, "initial_balance"),
            (self.transactions, tuple, "transactions"),
            (self.bets, tuple, "bets"),
            (self.settlements, tuple, "settlements"),
        )
        if not self.name.strip() or self.initial_balance.amount < 0:
            raise InvalidBankrollOperationError(
                "Banca exige nome e saldo inicial não negativo."
            )
        normalized_currency = self.currency.strip().upper()
        if self.initial_balance.currency != normalized_currency:
            raise InvalidBankrollOperationError("Moeda da banca diverge.")
        object.__setattr__(self, "currency", normalized_currency)
        _owned(self.transactions, BankrollTransaction, self.id)
        _owned(self.bets, Bet, self.id)
        _owned(self.settlements, Settlement, self.id)
        for items, money_field in (
            (self.transactions, "amount"),
            (self.bets, "stake"),
            (self.settlements, "return_amount"),
        ):
            if any(
                getattr(item, money_field).currency != self.currency
                for item in items
            ):
                raise InvalidBankrollOperationError(
                    "Registro financeiro utiliza moeda divergente."
                )
        if self.balance.amount < 0:
            raise InvalidBankrollOperationError("Saldo não pode ser negativo.")

    @property
    def balance(self) -> Money:
        amount = self.initial_balance.amount + sum(
            (transaction.signed_amount for transaction in self.transactions),
            Decimal("0"),
        )
        return Money(amount, self.currency)

    @property
    def open_exposure(self) -> Money:
        amount = sum(
            (
                bet.stake.amount
                for bet in self.bets
                if bet.status in {BetStatus.OPEN, BetStatus.PENDING}
            ),
            Decimal("0"),
        )
        return Money(amount, self.currency)

    def register_transaction(
        self,
        transaction: BankrollTransaction,
    ) -> Bankroll:
        return replace(
            self,
            transactions=(*self.transactions, transaction),
        )

    def place_bet(
        self,
        bet: Bet,
        stake_transaction: BankrollTransaction,
    ) -> Bankroll:
        if bet.stake.amount > self.balance.amount:
            raise InvalidBankrollOperationError("Saldo insuficiente.")
        if (
            stake_transaction.transaction_type
            is not TransactionType.BET_STAKE
            or stake_transaction.bet_id != bet.id
            or stake_transaction.amount != bet.stake
        ):
            raise InvalidBankrollOperationError(
                "Movimentação de stake incompatível."
            )
        return replace(
            self,
            bets=(*self.bets, bet),
            transactions=(*self.transactions, stake_transaction),
        )

    def settle(
        self,
        settlement: Settlement,
        return_transaction: BankrollTransaction | None = None,
    ) -> Bankroll:
        bet = next(
            (item for item in self.bets if item.id == settlement.bet_id),
            None,
        )
        if bet is None:
            raise InvalidBankrollOperationError(
                "A liquidação referencia aposta desconhecida."
            )
        if any(item.bet_id == bet.id for item in self.settlements):
            raise InvalidBankrollOperationError("Aposta já liquidada.")
        if settlement.return_amount.amount > 0:
            if (
                return_transaction is None
                or return_transaction.transaction_type
                is not TransactionType.BET_RETURN
                or return_transaction.bet_id != bet.id
                or return_transaction.amount != settlement.return_amount
            ):
                raise InvalidBankrollOperationError(
                    "Movimentação de retorno incompatível."
                )
        elif return_transaction is not None:
            raise InvalidBankrollOperationError(
                "Retorno zero não aceita movimentação."
            )
        status = BetStatus.parse(settlement.result.value)
        updated_bets = tuple(
            replace(item, status=status) if item.id == bet.id else item
            for item in self.bets
        )
        transactions = self.transactions + (
            (return_transaction,) if return_transaction is not None else ()
        )
        return replace(
            self,
            bets=updated_bets,
            settlements=(*self.settlements, settlement),
            transactions=transactions,
        )


def _types(*items: tuple[object, type, str]) -> None:
    for value, expected, field in items:
        if not isinstance(value, expected):
            raise TypeError(f"{field} deve ser {expected.__name__}.")


def _owned(
    items: tuple[object, ...],
    expected: type,
    bankroll_id: BankrollAccountId,
) -> None:
    ids: set[object] = set()
    for item in items:
        _types((item, expected, expected.__name__))
        if item.bankroll_id != bankroll_id or item.id in ids:
            raise InvalidBankrollOperationError(
                f"{expected.__name__} possui ownership ou identidade inválida."
            )
        ids.add(item.id)
