from sqlalchemy.orm import Session

from app.collectors import (
    SportsDataCollector,
)
from app.services.sports_sync_service import (
    SportsSyncService,
)
from app.services.sync_monitor_service import (
    SyncMonitorService,
)


class CollectorOrchestratorService:
    """
    Executa um collector e registra
    o histórico completo da operação.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

        self.sync_service = SportsSyncService(
            session
        )

        self.monitor_service = (
            SyncMonitorService(session)
        )

    def run(
        self,
        collector: SportsDataCollector,
        triggered_by: str = "manual",
    ) -> dict:
        sync_run = (
            self.monitor_service.start_run(
                source=collector.source_name,
                triggered_by=triggered_by,
            )
        )

        try:
            result = self.sync_service.sync_all(
                collector
            )

            completed_run = (
                self.monitor_service.mark_success(
                    sync_run_id=sync_run.id,
                    result=result,
                )
            )

            return {
                "sync_run_id": completed_run.id,
                "status": completed_run.status,
                "source": completed_run.source,
                "duration_seconds": (
                    completed_run.duration_seconds
                ),
                "result": result,
            }

        except Exception as error:
            self.session.rollback()

            failed_run = (
                self.monitor_service.mark_failed(
                    sync_run_id=sync_run.id,
                    error=error,
                )
            )

            raise RuntimeError(
                "A sincronização falhou. "
                f"Execução registrada com ID "
                f"{failed_run.id}: {error}"
            ) from error