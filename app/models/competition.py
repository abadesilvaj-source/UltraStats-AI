from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Competition(Base):
    """Representa uma competição esportiva."""

    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    season: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    sport: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="football",
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

    def __repr__(self) -> str:
        return (
            f"Competition(id={self.id}, "
            f"name='{self.name}', "
            f"season='{self.season}')"
        )