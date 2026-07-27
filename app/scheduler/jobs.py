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
from app.services.multi_provider_sync_service import MultiProviderSyncService

from app.services import SchedulerHeartbeatService


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

    - impede execuções simultâneas;
    - marca sincronizações antigas como falhas;
    - registra o início do job no heartbeat;
    - executa o collector;
    - registra sucesso ou falha;
    - libera a trava ao terminar.
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

    sync_session = None

    try:
        # Registra no heartbeat que o job começou.
        heartbeat_session = SessionLocal()

        try:
            heartbeat_service = (
                SchedulerHeartbeatService(
                    heartbeat_session
                )
            )

            heartbeat_service.register_job_started(
                settings.scheduler_instance_name
            )

        finally:
            heartbeat_session.close()

        # Verifica execuções antigas que ficaram presas.
        stale_count = mark_stale_runs()

        if stale_count > 0:
            logger.warning(
                "%s execução(ões) antiga(s) "
                "foram marcadas como failed.",
                stale_count,
            )

        sync_session = SessionLocal()
        if settings.sync_provider == "mock_provider":
            collector = MockSportsCollector(
                "data/providers/mock_sports_data.json"
            )
            orchestrator = CollectorOrchestratorService(
                sync_session
            )
            execution = orchestrator.run(
                collector=collector,
                triggered_by="scheduler",
            )
        elif settings.sync_provider == "multi_provider":
            execution = MultiProviderSyncService(
                sync_session
            ).run(triggered_by="scheduler")
        else:
            raise ValueError(
                "O provedor configurado não é suportado: "
                f"{settings.sync_provider}"
            )

        scheduler_state.last_job_status = (
            execution["status"]
        )

        # Registra no heartbeat que o job terminou
        # com sucesso.
        heartbeat_session = SessionLocal()

        try:
            heartbeat_service = (
                SchedulerHeartbeatService(
                    heartbeat_session
                )
            )

            heartbeat_service.register_job_finished(
                instance_name=(
                    settings.scheduler_instance_name
                ),
                status="success",
                error=None,
            )

        finally:
            heartbeat_session.close()

        logger.info(
            "Sincronização agendada concluída. "
            "Execução ID: %s | duração: %.4fs",
            execution["sync_run_id"],
            execution["duration_seconds"],
        )

    except Exception as error:
        scheduler_state.last_job_status = "failed"
        scheduler_state.last_error = str(error)

        # Registra no heartbeat que o job terminou
        # com falha.
        heartbeat_session = SessionLocal()

        try:
            heartbeat_service = (
                SchedulerHeartbeatService(
                    heartbeat_session
                )
            )

            heartbeat_service.register_job_finished(
                instance_name=(
                    settings.scheduler_instance_name
                ),
                status="failed",
                error=str(error),
            )

        except Exception:
            heartbeat_session.rollback()

            logger.exception(
                "Também ocorreu um erro ao registrar "
                "a falha no heartbeat."
            )

        finally:
            heartbeat_session.close()

        logger.exception(
            "Erro na sincronização agendada: %s",
            error,
        )

    finally:
        if sync_session is not None:
           sync_session.close()

        scheduler_state.current_job_running = False
        scheduler_state.last_job_finished_at = (
            datetime.now()
        )

        scheduler_lock.release()


def run_scheduled_live_sync() -> None:
    """Executa o coletor leve de placares sem bloquear o pipeline completo."""
    lock_acquired = scheduler_lock.acquire(blocking=False)
    if not lock_acquired:
        logger.info(
            "Atualização ao vivo adiada: outra sincronização está ativa."
        )
        return

    session = None
    try:
        if settings.sync_provider != "multi_provider":
            return
        session = SessionLocal()
        execution = MultiProviderSyncService(session).run_live(
            triggered_by="scheduler"
        )
        logger.info(
            "Atualização ao vivo concluída. Execução ID: %s | "
            "fontes=%s | salvos=%s | degradada=%s",
            execution["sync_run_id"],
            ",".join(execution["successful_sources"]),
            execution["saved"],
            execution["degraded"],
        )
    except Exception as error:
        logger.exception(
            "Erro na atualização leve ao vivo: %s", error
        )
    finally:
        if session is not None:
            session.close()
        scheduler_lock.release()
        
def update_scheduler_heartbeat() -> None:
    """
    Atualiza o sinal de vida persistente do scheduler.

    Se a instância ainda não estiver registrada,
    registra seu início automaticamente.
    """

    session = SessionLocal()

    try:
        service = SchedulerHeartbeatService(
            session
        )

        try:
            service.register_heartbeat(
                settings.scheduler_instance_name
            )

        except ValueError:
            service.register_start(
                instance_name=(
                    settings.scheduler_instance_name
                ),
                provider=settings.sync_provider,
            )

        logger.debug(
            "Heartbeat atualizado | instância=%s",
            settings.scheduler_instance_name,
        )

    except Exception as error:
        session.rollback()

        logger.exception(
            "Erro ao atualizar heartbeat: %s",
            error,
        )

    finally:
        session.close()
