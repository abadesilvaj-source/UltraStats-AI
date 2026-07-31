from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MatchStatistics(Base):
    """Armazena as estatísticas oficiais de uma partida."""

    __tablename__ = "match_statistics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    corners_home: Mapped[int | None] = mapped_column(Integer, nullable=True)
    corners_away: Mapped[int | None] = mapped_column(Integer, nullable=True)

    yellow_cards_home: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    yellow_cards_away: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    red_cards_home: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    red_cards_away: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    shots_home: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shots_away: Mapped[int | None] = mapped_column(Integer, nullable=True)

    shots_on_target_home: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    shots_on_target_away: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    offsides_home: Mapped[int | None] = mapped_column(Integer, nullable=True)
    offsides_away: Mapped[int | None] = mapped_column(Integer, nullable=True)

    possession_home: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    possession_away: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    xg_home: Mapped[float | None] = mapped_column(Float, nullable=True)
    xg_away: Mapped[float | None] = mapped_column(Float, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    def __repr__(self) -> str:
        return (
            f"MatchStatistics("
            f"match_id={self.match_id}, "
            f"corners={self.corners_home}+{self.corners_away})"
        )