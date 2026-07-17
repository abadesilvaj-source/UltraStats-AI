from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import Base


class SchedulerHeartbeat(Base):
    """
    Representa o estado persistente
    de uma instância do scheduler.
    """

    __tablename__ = "scheduler_heartbeats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    instance_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="starting",
        index=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    process_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    hostname: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    last_heartbeat_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        index=True,
    )

    stopped_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_job_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    last_job_started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_job_finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    def __repr__(self) -> str:
        return (
            f"SchedulerHeartbeat("
            f"id={self.id}, "
            f"instance_name='{self.instance_name}', "
            f"status='{self.status}')"
        )