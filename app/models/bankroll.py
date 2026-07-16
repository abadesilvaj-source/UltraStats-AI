from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Bankroll(Base):
    """Representa uma banca do UltraStats AI."""

    __tablename__ = "bankrolls"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="BRL",
    )

    initial_balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    current_balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    unit_percentage: Mapped[float] = mapped_column(
        nullable=False,
        default=1.0,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    def __repr__(self) -> str:
        return (
            f"Bankroll(id={self.id}, "
            f"name='{self.name}', "
            f"balance={self.current_balance})"
        )