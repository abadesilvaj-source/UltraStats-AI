from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Bet(Base):
    """Representa uma aposta registrada no UltraStats AI."""

    __tablename__ = "bets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    prediction_id: Mapped[int | None] = mapped_column(
        ForeignKey("predictions.id"),
        nullable=True,
        index=True,
    )

    bankroll_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "bankrolls.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id"),
        nullable=False,
        index=True,
    )

    market_id: Mapped[int] = mapped_column(
        ForeignKey("markets.id"),
        nullable=False,
        index=True,
    )

    selection: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    odd_value: Mapped[Decimal] = mapped_column(
        Numeric(8, 3),
        nullable=False,
    )

    stake_units: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    stake_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )

    payout_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )

    result: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    profit_units: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    is_official: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    placed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    settled_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"Bet(id={self.id}, "
            f"selection='{self.selection}', "
            f"status='{self.status}')"
        )