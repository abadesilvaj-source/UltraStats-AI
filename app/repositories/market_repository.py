from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Market


class MarketRepository:
    """Operações de banco relacionadas aos mercados."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_code(
        self,
        code: str,
    ) -> Market | None:
        statement = select(Market).where(
            Market.code == code
        )

        return self.session.scalar(statement)

    def list_all(self) -> list[Market]:
        statement = select(Market).order_by(
            Market.category,
            Market.name,
        )

        return list(
            self.session.scalars(statement).all()
        )