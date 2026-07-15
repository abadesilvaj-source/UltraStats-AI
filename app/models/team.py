from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    league: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    power_rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=50.0,
    )

    attack_rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=50.0,
    )

    defense_rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=50.0,
    )

    corner_rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=50.0,
    )

    card_rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=50.0,
    )

    goal_rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=50.0,
    )

    offside_rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=50.0,
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
            f"Team(id={self.id}, "
            f"name='{self.name}', "
            f"power_rating={self.power_rating})"
        )