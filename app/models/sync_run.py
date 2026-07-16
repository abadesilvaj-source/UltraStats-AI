from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SyncRun(Base):
    """
    Representa uma execução de sincronização
    com um provedor esportivo.
    """

    __tablename__ = "sync_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        index=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    competitions_created: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    competitions_updated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    competitions_linked: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    teams_created: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    teams_updated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    teams_linked: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    matches_created: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    matches_updated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    matches_skipped: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    triggered_by: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="manual",
    )

    def __repr__(self) -> str:
        return (
            f"SyncRun(id={self.id}, "
            f"source='{self.source}', "
            f"status='{self.status}')"
        )