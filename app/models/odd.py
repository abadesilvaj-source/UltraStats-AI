from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Odd(Base):
    """Representa uma cotação oferecida por uma casa de apostas."""

    __tablename__ = "odds"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    market_id: Mapped[int] = mapped_column(
        ForeignKey("markets.id"),
        nullable=False,
        index=True,
    )

    bookmaker: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    selection: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    odd_value: Mapped[Decimal] = mapped_column(
        Numeric(8, 3),
        nullable=False,
    )

    is_closing: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"Odd(id={self.id}, "
            f"bookmaker='{self.bookmaker}', "
            f"selection='{self.selection}', "
            f"odd={self.odd_value})"
        )