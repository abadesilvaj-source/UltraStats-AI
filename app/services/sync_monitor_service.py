from datetime import datetime

from sqlalchemy.orm import Session

from app.models import SyncRun
from app.repositories import (
    SyncRunRepository,
)


class SyncMonitorService:
    """
    Gerencia o histórico das execuções
    de sincronização.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

        self.repository = SyncRunRepository(
            session
        )

    def start_run(
        self,
        source: str,
        triggered_by: str = "manual",
    ) -> SyncRun:
        if not source.strip():
            raise ValueError(
                "A fonte da sincronização é obrigatória."
            )

        sync_run = SyncRun(
            source=source.strip(),
            status="started",
            started_at=datetime.now(),
            finished_at=None,
            duration_seconds=None,
            competitions_created=0,
            competitions_updated=0,
            competitions_linked=0,
            teams_created=0,
            teams_updated=0,
            teams_linked=0,
            matches_created=0,
            matches_updated=0,
            matches_skipped=0,
            error_message=None,
            triggered_by=triggered_by,
        )

        self.repository.create(
            sync_run
        )

        self.session.commit()
        self.session.refresh(sync_run)

        return sync_run

    def mark_success(
        self,
        sync_run_id: int,
        result: dict,
    ) -> SyncRun:
        sync_run = self.repository.find_by_id(
            sync_run_id
        )

        if not sync_run:
            raise ValueError(
                "Execução de sincronização não encontrada."
            )

        finished_at = datetime.now()

        sync_run.status = "success"
        sync_run.finished_at = finished_at
        sync_run.duration_seconds = (
            finished_at
            - sync_run.started_at
        ).total_seconds()

        competitions = result.get(
            "competitions",
            {},
        )

        teams = result.get(
            "teams",
            {},
        )

        matches = result.get(
            "matches",
            {},
        )

        sync_run.competitions_created = int(
            competitions.get(
                "created",
                0,
            )
        )

        sync_run.competitions_updated = int(
            competitions.get(
                "updated",
                0,
            )
        )

        sync_run.competitions_linked = int(
            competitions.get(
                "linked",
                0,
            )
        )

        sync_run.teams_created = int(
            teams.get(
                "created",
                0,
            )
        )

        sync_run.teams_updated = int(
            teams.get(
                "updated",
                0,
            )
        )

        sync_run.teams_linked = int(
            teams.get(
                "linked",
                0,
            )
        )

        sync_run.matches_created = int(
            matches.get(
                "created",
                0,
            )
        )

        sync_run.matches_updated = int(
            matches.get(
                "updated",
                0,
            )
        )

        sync_run.matches_skipped = int(
            matches.get(
                "skipped",
                0,
            )
        )

        sync_run.error_message = None

        self.repository.update(
            sync_run
        )

        self.session.commit()
        self.session.refresh(sync_run)

        return sync_run

    def mark_failed(
        self,
        sync_run_id: int,
        error: Exception | str,
    ) -> SyncRun:
        sync_run = self.repository.find_by_id(
            sync_run_id
        )

        if not sync_run:
            raise ValueError(
                "Execução de sincronização não encontrada."
            )

        finished_at = datetime.now()

        sync_run.status = "failed"
        sync_run.finished_at = finished_at
        sync_run.duration_seconds = (
            finished_at
            - sync_run.started_at
        ).total_seconds()

        error_message = str(error).strip()

        if not error_message:
            error_message = (
                "Erro não informado."
            )

        sync_run.error_message = (
            error_message[:2000]
        )

        self.repository.update(
            sync_run
        )

        self.session.commit()
        self.session.refresh(sync_run)

        return sync_run

    def list_recent_runs(
        self,
        limit: int = 50,
    ) -> list[SyncRun]:
        return self.repository.list_recent(
            limit=limit
        )

    def get_latest_run(
        self,
        source: str,
    ) -> SyncRun | None:
        return (
            self.repository
            .find_latest_by_source(
                source
            )
        )