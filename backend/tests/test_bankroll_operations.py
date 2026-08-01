import pytest

from app.database.session import SessionLocal
from app.services import BankrollService


def test_create_bankroll_requires_name() -> None:
    session = SessionLocal()
    try:
        with pytest.raises(ValueError, match="nome da banca"):
            BankrollService(session).create_bankroll(
                name="  ",
                initial_balance=1000,
            )
    finally:
        session.close()


def test_deposit_rejects_zero() -> None:
    session = SessionLocal()

    try:
        service = BankrollService(session)

        with pytest.raises(ValueError):
            service.deposit(
                bankroll_id=1,
                amount=0,
            )

    finally:
        session.close()


def test_withdraw_rejects_zero() -> None:
    session = SessionLocal()

    try:
        service = BankrollService(session)

        with pytest.raises(ValueError):
            service.withdraw(
                bankroll_id=1,
                amount=0,
            )

    finally:
        session.close()


def test_manual_adjustment_rejects_zero() -> None:
    session = SessionLocal()

    try:
        service = BankrollService(session)

        with pytest.raises(ValueError):
            service.manual_adjustment(
                bankroll_id=1,
                amount=0,
                description="Teste",
            )

    finally:
        session.close()


def test_manual_adjustment_requires_description() -> None:
    session = SessionLocal()

    try:
        service = BankrollService(session)

        with pytest.raises(ValueError):
            service.manual_adjustment(
                bankroll_id=1,
                amount=10,
                description="",
            )

    finally:
        session.close()
