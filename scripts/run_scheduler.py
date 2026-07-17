import logging
import threading
import time

from app.core.config import settings
from app.core.logging_config import (
    configure_logging,
)

from app.database.session import SessionLocal
from app.scheduler import (
    SchedulerService,
    run_scheduled_sync,
    update_scheduler_heartbeat,
)
from app.services import (
    SchedulerHeartbeatService,
)

def run_heartbeat_loop(
    stop_event: threading.Event,
) -> None:
    """
    Atualiza o heartbeat continuamente,
    independentemente dos jobs de sincronização.
    """

    logger = logging.getLogger(
        "ultrastats.scheduler.heartbeat"
    )

    while not stop_event.is_set():
        try:
            update_scheduler_heartbeat()

        except Exception as error:
            logger.exception(
                "Erro no loop de heartbeat: %s",
                error,
            )

        stop_event.wait(
            settings.scheduler_heartbeat_seconds
        )

def main() -> None:
    logger = configure_logging(
        service_name="scheduler"
    )

    if not settings.sync_enabled:
        logger.warning(
            "Scheduler desativado pela configuração."
        )
        return

    # Registra no banco que a instância iniciou.
    heartbeat_session = SessionLocal()

    try:
        heartbeat_service = (
            SchedulerHeartbeatService(
                heartbeat_session
            )
        )

        heartbeat_service.register_start(
            instance_name=(
                settings.scheduler_instance_name
            ),
            provider=settings.sync_provider,
        )

    finally:
        heartbeat_session.close()

    heartbeat_stop_event = threading.Event()

    heartbeat_thread = threading.Thread(
        target=run_heartbeat_loop,
        args=(heartbeat_stop_event,),
        name="scheduler-heartbeat",
        daemon=True,
    )

    heartbeat_thread.start()

    scheduler = SchedulerService()

    # Job principal de sincronização esportiva.
    scheduler.add_interval_job(
        func=run_scheduled_sync,
        minutes=(
            settings.sync_interval_minutes
        ),
        job_id="sports_data_sync",
        run_immediately=True,
    )

    scheduler.start()

    logger.info(
        "Scheduler iniciado | "
        "instância=%s | "
        "provedor=%s | "
        "intervalo_sync=%s minuto(s) | "
        "intervalo_heartbeat=%s segundo(s)",
        settings.scheduler_instance_name,
        settings.sync_provider,
        settings.sync_interval_minutes,
        settings.scheduler_heartbeat_seconds,
    )

    logger.info(
        "Scheduler aguardando execuções."
    )

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info(
            "Solicitação de encerramento recebida."
        )



    finally:

        heartbeat_stop_event.set()

        heartbeat_thread.join(
            timeout=5
        )
        
        heartbeat_session = SessionLocal()

        try:
            heartbeat_service = (
                SchedulerHeartbeatService(
                    heartbeat_session
                )
            )

            heartbeat_service.register_stop(
                settings.scheduler_instance_name
            )

        except Exception as error:
            heartbeat_session.rollback()

            logger.exception(
                "Erro ao registrar parada: %s",
                error,
            )

        finally:
            heartbeat_session.close()

        scheduler.shutdown()

        logger.info(
            "Scheduler encerrado."
        )

if __name__ == "__main__":
    main()