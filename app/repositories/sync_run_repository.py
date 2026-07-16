from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SyncRun


class SyncRunRepository:
    """
    Operações de banco relacionadas
    ao histórico de sincronizações.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def create(
        self,
        sync_run: SyncRun,
    ) -> SyncRun:
        self.session.add(
            sync_run
        )

        self.session.flush()

        return sync_run

    def update(
        self,
        sync_run: SyncRun,
    ) -> SyncRun:
        self.session.flush()

        return sync_run

    def find_by_id(
        self,
        sync_run_id: int,
    ) -> SyncRun | None:
        return self.session.get(
            SyncRun,
            sync_run_id,
        )

    def list_recent(
        self,
        limit: int = 50,
    ) -> list[SyncRun]:
        statement = (
            select(SyncRun)
            .order_by(
                SyncRun.started_at.desc(),
                SyncRun.id.desc(),
            )
            .limit(limit)
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def find_latest_by_source(
        self,
        source: str,
    ) -> SyncRun | None:
        statement = (
            select(SyncRun)
            .where(
                SyncRun.source == source
            )
            .order_by(
                SyncRun.started_at.desc(),
                SyncRun.id.desc(),
            )
            .limit(1)
        )

        return self.session.scalar(
            statement
        )