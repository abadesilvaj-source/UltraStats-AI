import logging
from datetime import datetime, timedelta

from sqlalchemy import select

from app.collectors import MockSportsCollector
from app.core.config import settings
from app.database.session import SessionLocal
from app.models import SyncRun
from app.scheduler.scheduler_state import (
    scheduler_lock,
    scheduler_state,
)
from app.services import CollectorOrchestratorService


logger = logging.getLogger(
    "ultrastats.scheduler"
)


def mark_stale_runs() -> int:
    """
    Marca como failed sincronizações que ficaram
    presas em status started por tempo excessivo.
    """

    session = SessionLocal()

    try:
        limit_time = (
            datetime.now()
            - timedelta(
                minutes=(
                    settings
                    .sync_max_runtime_minutes
                )
            )
        )

        statement = select(
            SyncRun
        ).where(
            SyncRun.status == "started",
            SyncRun.started_at < limit_time,
        )

        stale_runs = list(
            session.scalars(
                statement
            ).all()
        )

        for run in stale_runs:
            run.status = "failed"
            run.finished_at = datetime.now()

            run.duration_seconds = (
                run.finished_at
                - run.started_at
            ).total_seconds()

            run.error_message = (
                "Execução marcada automaticamente "
                "como falha por exceder o tempo máximo."
            )

        if stale_runs:
            session.commit()

        return len(stale_runs)

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def run_scheduled_sync() -> None:
    """
    Executa a sincronização automática.

    Esta função:
    - impede execução simultânea;
    - detecta execuções antigas travadas;
    - executa o collector;
    - registra sucesso ou falha.
    """

    lock_acquired = scheduler_lock.acquire(
        blocking=False
    )

    if not lock_acquired:
        logger.warning(
            "Sincronização ignorada: "
            "já existe uma execução em andamento."
        )
        return

    scheduler_state.current_job_running = True
    scheduler_state.last_job_started_at = datetime.now()
    scheduler_state.last_job_status = "running"
    scheduler_state.last_error = None

    session = None

    try:
        stale_count = mark_stale_runs()

        if stale_count > 0:
            logger.warning(
                "%s execução(ões) antiga(s) "
                "foram marcadas como failed.",
                stale_count,
            )

        if settings.sync_provider != "mock_provider":
            raise ValueError(
                "O provedor configurado ainda não "
                f"é suportado: {settings.sync_provider}"
            )

        collector = MockSportsCollector(
            "data/providers/mock_sports_data.json"
        )

        session = SessionLocal()

        orchestrator = CollectorOrchestratorService(
            session
        )

        execution = orchestrator.run(
            collector=collector,
            triggered_by="scheduler",
        )

        scheduler_state.last_job_status = (
            execution["status"]
        )

        logger.info(
            "Sincronização agendada concluída. "
            "Execução ID: %s | duração: %.4fs",
            execution["sync_run_id"],
            execution[
                "duration_seconds"
            ],
        )

    except Exception as error:
        scheduler_state.last_job_status = "failed"
        scheduler_state.last_error = str(error)

        logger.exception(
            "Erro na sincronização agendada: %s",
            error,
        )

    finally:
        if session is not None:
            session.close()

        scheduler_state.current_job_running = False
        scheduler_state.last_job_finished_at = (
            datetime.now()
        )

        scheduler_lock.release()