from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Match, Odd


class ClosingOddsService:
    """Congela a última cotação pré-jogo para avaliação de CLV."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def mark(self, now: datetime | None = None) -> int:
        current = now or datetime.now()
        closing_odd_exists = (
            select(Odd.id)
            .where(
                Odd.match_id == Match.id,
                Odd.is_closing.is_(True),
            )
            .exists()
        )
        matches = self.session.scalars(
            select(Match).where(
                Match.kickoff_at <= current,
                Match.kickoff_at >= current - timedelta(days=2),
                Match.status.in_(("in_progress", "finished")),
                ~closing_odd_exists,
            )
        ).all()
        marked = 0
        for match in matches:
            rows = self.session.scalars(
                select(Odd).where(
                    Odd.match_id == match.id,
                    Odd.collected_at <= match.kickoff_at,
                    Odd.odd_value > 1,
                ).order_by(Odd.collected_at.desc())
            ).all()
            latest: dict[tuple[int, str, str], Odd] = {}
            for odd in rows:
                latest.setdefault(
                    (odd.market_id, odd.bookmaker, odd.selection.casefold()),
                    odd,
                )
            for odd in latest.values():
                odd.is_closing = True
                marked += 1
        return marked
