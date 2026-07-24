"""Testes do Aggregate Root Bankroll."""

from dataclasses import replace

import pytest

from ultrastats_ai.domain.bankroll import (
    Bankroll,
    BankrollTransaction,
    Bet,
    BetLeg,
    InvalidBankrollOperationError,
    Settlement,
    SettlementResult,
    TransactionType,
)
from ultrastats_ai.domain.shared import (
    BankrollAccountId,
    BankrollTransactionId,
    BetId,
    BetLegId,
    BettingMarketId,
    BettingSelectionId,
    BetStatus,
    BookmakerId,
    Money,
    Odds,
    SettlementId,
    UtcTimestamp,
)


NOW = UtcTimestamp("2026-08-01T12:00:00Z")


def transaction(
    bankroll_id: BankrollAccountId,
    transaction_type: TransactionType,
    amount: str,
    *,
    bet_id: BetId | None = None,
) -> BankrollTransaction:
    return BankrollTransaction(
        BankrollTransactionId.new(),
        bankroll_id,
        transaction_type,
        Money(amount, "BRL"),
        NOW,
        transaction_type.value,
        bet_id,
    )


def bet(
    bankroll_id: BankrollAccountId,
    *,
    stake: str = "100",
) -> Bet:
    bet_id = BetId.new()
    leg = BetLeg(
        BetLegId.new(),
        bet_id,
        BettingMarketId.new(),
        BettingSelectionId.new(),
        Odds("2"),
    )
    return Bet(
        bet_id,
        bankroll_id,
        BookmakerId.new(),
        Money(stake, "BRL"),
        Odds("2"),
        BetStatus.OPEN,
        NOW,
        (leg,),
    )


def bankroll() -> Bankroll:
    return Bankroll(
        BankrollAccountId.new(),
        "Principal",
        "BRL",
        Money("1000", "BRL"),
    )


def test_transactions_update_balance_with_credit_and_debit() -> None:
    account = bankroll()
    credited = account.register_transaction(
        transaction(account.id, TransactionType.DEPOSIT, "100")
    )
    debited = credited.register_transaction(
        transaction(account.id, TransactionType.WITHDRAWAL, "50")
    )

    assert credited.balance.amount == 1100
    assert debited.balance.amount == 1050


def test_transaction_requires_positive_amount_and_description() -> None:
    item = transaction(
        BankrollAccountId.new(),
        TransactionType.DEPOSIT,
        "10",
    )

    with pytest.raises(InvalidBankrollOperationError):
        replace(item, amount=Money("0", "BRL"))
    with pytest.raises(InvalidBankrollOperationError):
        replace(item, description=" ")
    with pytest.raises(TypeError, match="bet_id"):
        replace(item, bet_id=object())  # type: ignore[arg-type]


def test_bet_validates_legs_stake_and_combined_odds() -> None:
    item = bet(BankrollAccountId.new())
    assert item.legs[0].status is BetStatus.PENDING

    with pytest.raises(InvalidBankrollOperationError, match="stake"):
        replace(item, stake=Money("0", "BRL"))
    with pytest.raises(TypeError, match="leg"):
        replace(item, legs=(object(),))  # type: ignore[arg-type]
    with pytest.raises(InvalidBankrollOperationError, match="Perna"):
        replace(item, legs=(replace(item.legs[0], bet_id=BetId.new()),))
    with pytest.raises(InvalidBankrollOperationError, match="Perna"):
        replace(item, legs=(item.legs[0], item.legs[0]))
    with pytest.raises(InvalidBankrollOperationError, match="combinada"):
        replace(item, odds=Odds("3"))


def test_bankroll_places_bet_and_tracks_exposure() -> None:
    account = bankroll()
    wager = bet(account.id)
    stake = transaction(
        account.id,
        TransactionType.BET_STAKE,
        "100",
        bet_id=wager.id,
    )

    updated = account.place_bet(wager, stake)

    assert updated.balance.amount == 900
    assert updated.open_exposure.amount == 100


def test_place_bet_validates_funds_and_transaction() -> None:
    account = bankroll()
    expensive = bet(account.id, stake="1100")
    valid = bet(account.id)

    with pytest.raises(InvalidBankrollOperationError, match="insuficiente"):
        account.place_bet(
            expensive,
            transaction(
                account.id,
                TransactionType.BET_STAKE,
                "1100",
                bet_id=expensive.id,
            ),
        )
    with pytest.raises(InvalidBankrollOperationError, match="stake"):
        account.place_bet(
            valid,
            transaction(
                account.id,
                TransactionType.DEPOSIT,
                "100",
                bet_id=valid.id,
            ),
        )


def placed_bankroll() -> tuple[Bankroll, Bet]:
    account = bankroll()
    wager = bet(account.id)
    return (
        account.place_bet(
            wager,
            transaction(
                account.id,
                TransactionType.BET_STAKE,
                "100",
                bet_id=wager.id,
            ),
        ),
        wager,
    )


def settlement(
    account: Bankroll,
    wager: Bet,
    *,
    result: SettlementResult = SettlementResult.WON,
    return_amount: str = "200",
) -> Settlement:
    return Settlement(
        SettlementId.new(),
        account.id,
        wager.id,
        result,
        Money(return_amount, "BRL"),
        NOW,
        "Regra padrão",
    )


def test_winning_settlement_updates_bet_and_balance() -> None:
    account, wager = placed_bankroll()
    result = settlement(account, wager)
    returned = transaction(
        account.id,
        TransactionType.BET_RETURN,
        "200",
        bet_id=wager.id,
    )

    updated = account.settle(result, returned)

    assert updated.balance.amount == 1100
    assert updated.bets[0].status is BetStatus.WON
    assert updated.open_exposure.amount == 0


def test_losing_settlement_needs_no_return_transaction() -> None:
    account, wager = placed_bankroll()
    result = settlement(
        account,
        wager,
        result=SettlementResult.LOST,
        return_amount="0",
    )

    updated = account.settle(result)

    assert updated.balance.amount == 900
    assert updated.bets[0].status is BetStatus.LOST


def test_settlement_validates_reference_duplicate_and_return() -> None:
    account, wager = placed_bankroll()
    unknown = replace(
        settlement(account, wager, return_amount="0"),
        bet_id=BetId.new(),
    )
    with pytest.raises(InvalidBankrollOperationError, match="desconhecida"):
        account.settle(unknown)

    won = settlement(account, wager)
    with pytest.raises(InvalidBankrollOperationError, match="retorno"):
        account.settle(won)

    lost = settlement(
        account,
        wager,
        result=SettlementResult.LOST,
        return_amount="0",
    )
    with pytest.raises(InvalidBankrollOperationError, match="Retorno zero"):
        account.settle(
            lost,
            transaction(
                account.id,
                TransactionType.BET_RETURN,
                "1",
                bet_id=wager.id,
            ),
        )

    settled = account.settle(
        won,
        transaction(
            account.id,
            TransactionType.BET_RETURN,
            "200",
            bet_id=wager.id,
        ),
    )
    with pytest.raises(InvalidBankrollOperationError, match="já liquidada"):
        settled.settle(won)


def test_settlement_requires_rule_and_nonnegative_return() -> None:
    account, wager = placed_bankroll()
    item = settlement(account, wager)

    with pytest.raises(InvalidBankrollOperationError):
        replace(item, rule="")
    with pytest.raises(InvalidBankrollOperationError):
        replace(item, return_amount=Money("-1", "BRL"))


def test_bankroll_validates_currency_ownership_identity_and_balance() -> None:
    account = bankroll()
    credit = transaction(
        account.id,
        TransactionType.DEPOSIT,
        "10",
    )

    with pytest.raises(InvalidBankrollOperationError, match="nome"):
        replace(account, name="")
    with pytest.raises(InvalidBankrollOperationError, match="Moeda"):
        replace(account, currency="USD")
    assert replace(account, currency="brl").currency == "BRL"
    with pytest.raises(InvalidBankrollOperationError, match="ownership"):
        replace(
            account,
            transactions=(
                replace(credit, bankroll_id=BankrollAccountId.new()),
            ),
        )
    with pytest.raises(InvalidBankrollOperationError, match="ownership"):
        replace(account, transactions=(credit, credit))
    with pytest.raises(InvalidBankrollOperationError, match="Saldo"):
        replace(
            account,
            transactions=(
                transaction(
                    account.id,
                    TransactionType.WITHDRAWAL,
                    "1001",
                ),
            ),
        )
    with pytest.raises(InvalidBankrollOperationError, match="moeda divergente"):
        replace(
            account,
            transactions=(
                replace(credit, amount=Money("10", "USD")),
            ),
        )


def test_type_validation_for_bankroll_helpers() -> None:
    with pytest.raises(TypeError, match="id"):
        replace(bankroll(), id=object())  # type: ignore[arg-type]
    account = bankroll()
    with pytest.raises(TypeError, match="BankrollTransaction"):
        replace(
            account,
            transactions=(object(),),  # type: ignore[arg-type]
        )
