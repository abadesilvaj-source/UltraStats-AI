from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Match(Base):
    """Representa uma partida esportiva."""

    __tablename__ = "matches"
    __table_args__ = (
        Index("ix_matches_status_kickoff", "status", "kickoff_at"),
        Index(
            "ix_matches_home_status_kickoff",
            "home_team_id", "status", "kickoff_at",
        ),
        Index(
            "ix_matches_away_status_kickoff",
            "away_team_id", "status", "kickoff_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"),
        nullable=False,
        index=True,
    )

    home_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
    )

    away_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
    )

    kickoff_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="scheduled",
    )

    home_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    away_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    venue: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
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
            f"Match(id={self.id}, "
            f"home_team_id={self.home_team_id}, "
            f"away_team_id={self.away_team_id}, "
            f"status='{self.status}')"
        )
