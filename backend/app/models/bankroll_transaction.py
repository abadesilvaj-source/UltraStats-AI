from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BankrollTransaction(Base):
    """Representa uma movimentação financeira da banca."""

    __tablename__ = "bankroll_transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    bankroll_id: Mapped[int] = mapped_column(
        ForeignKey(
            "bankrolls.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    bet_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "bets.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    slip_id: Mapped[int | None] = mapped_column(
        ForeignKey("bet_slips.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    balance_before: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    balance_after: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"BankrollTransaction("
            f"id={self.id}, "
            f"type='{self.transaction_type}', "
            f"amount={self.amount})"
        )
