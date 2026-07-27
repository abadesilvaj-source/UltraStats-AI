from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class BetSlip(Base):
    """Bilhete simples ou múltiplo registrado pelo usuário."""

    __tablename__ = "bet_slips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bankroll_id: Mapped[int] = mapped_column(
        ForeignKey("bankrolls.id"), nullable=False, index=True
    )
    bookmaker: Mapped[str] = mapped_column(String(100), nullable=False)
    kind: Mapped[str] = mapped_column(String(20), nullable=False)
    stake_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    total_odds: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    potential_return: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="pending", index=True
    )
    payout_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    placed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )
    settled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    legs: Mapped[list["BetLeg"]] = relationship(
        back_populates="slip", cascade="all, delete-orphan"
    )


class BetLeg(Base):
    """Seleção individual de um bilhete."""

    __tablename__ = "bet_legs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slip_id: Mapped[int] = mapped_column(
        ForeignKey("bet_slips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id"), nullable=False, index=True
    )
    market_id: Mapped[int] = mapped_column(
        ForeignKey("markets.id"), nullable=False
    )
    prediction_id: Mapped[int | None] = mapped_column(
        ForeignKey("predictions.id"), nullable=True
    )
    selection: Mapped[str] = mapped_column(String(150), nullable=False)
    odd_value: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="pending"
    )
    result: Mapped[str | None] = mapped_column(String(30), nullable=True)
    settled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    slip: Mapped[BetSlip] = relationship(back_populates="legs")
