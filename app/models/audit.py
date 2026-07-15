from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Audit(Base):
    """Registra a auditoria pós-jogo das previsões."""

    __tablename__ = "audits"

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

    prediction_id: Mapped[int | None] = mapped_column(
        ForeignKey("predictions.id"),
        nullable=True,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    result_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    predicted_probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    calibrated_probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    audited_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    def __repr__(self) -> str:
        return (
            f"Audit(id={self.id}, "
            f"match_id={self.match_id}, "
            f"result_status='{self.result_status}')"
        )