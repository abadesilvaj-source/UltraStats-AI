from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MatchStatistics


class MatchStatisticsRepository:
    """
    Operações de banco relacionadas
    às estatísticas oficiais da partida.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_match_id(
        self,
        match_id: int,
    ) -> MatchStatistics | None:
        statement = select(MatchStatistics).where(
            MatchStatistics.match_id == match_id
        )

        return self.session.scalar(statement)

    def create(
        self,
        statistics: MatchStatistics,
    ) -> MatchStatistics:
        self.session.add(statistics)
        self.session.flush()

        return statistics

    def update(
        self,
        statistics: MatchStatistics,
    ) -> MatchStatistics:
        self.session.flush()

        return statistics