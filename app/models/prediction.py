from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Prediction(Base):
    """Armazena uma previsão produzida pelo UltraStats AI."""

    __tablename__ = "predictions"

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

    selection: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    probability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    implied_probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    expected_value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    uqs: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    use_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    confluence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    evidence_level: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    risk_level: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"Prediction(id={self.id}, "
            f"selection='{self.selection}', "
            f"probability={self.probability})"
        )