import logging
import time

from app.core.config import settings
from app.core.logging_config import (
    configure_collector_logging,
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


def main() -> None:
    configure_collector_logging()

    logger = logging.getLogger(
        "ultrastats.scheduler"
    )

    if not settings.sync_enabled:
        print(
            "Scheduler desativado pelo .env."
        )
        return

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

    scheduler = SchedulerService()

    scheduler.add_interval_job(
        func=run_scheduled_sync,
        minutes=(
            settings.sync_interval_minutes
        ),
        job_id="sports_data_sync",
        run_immediately=True,
    )

    scheduler.add_seconds_job(
        func=update_scheduler_heartbeat,
        seconds=(
            settings.scheduler_heartbeat_seconds
        ),
        job_id="scheduler_heartbeat",
        run_immediately=True,
    )

    scheduler.start()

    print("\nSCHEDULER INICIADO")
    print("=" * 60)

    print(
        f"Provedor: "
        f"{settings.sync_provider}"
    )

    print(
        f"Intervalo: "
        f"{settings.sync_interval_minutes} minuto(s)"
    )

    print(
        f"Tempo máximo: "
        f"{settings.sync_max_runtime_minutes} minuto(s)"
    )

    print(
        "Pressione Ctrl+C para encerrar."
    )

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print(
            "\nEncerrando scheduler..."
        )

    finally:
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

        print(
            "Scheduler encerrado com sucesso."
        )


if __name__ == "__main__":
    main()