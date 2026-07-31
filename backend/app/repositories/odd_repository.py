from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Odd


class OddRepository:
    """Operações de banco relacionadas às odds."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, odd: Odd) -> Odd:
        self.session.add(odd)
        self.session.flush()

        return odd

    def find_latest(
        self,
        match_id: int,
        market_id: int,
        selection: str,
    ) -> Odd | None:
        statement = (
            select(Odd)
            .where(
                Odd.match_id == match_id,
                Odd.market_id == market_id,
                Odd.selection == selection,
            )
            .order_by(Odd.collected_at.desc())
        )

        return self.session.scalar(statement)