from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
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

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    auto_core: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    promotion_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="observation",
    )

    promotion_qualified_since: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    promotion_evaluated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    promotion_metrics: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
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
