import logging
import time

from app.core.config import settings
from app.core.logging_config import (
    configure_collector_logging,
)
from app.scheduler import (
    SchedulerService,
    run_scheduled_sync,
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

    scheduler = SchedulerService()

    scheduler.add_interval_job(
        func=run_scheduled_sync,
        minutes=(
            settings.sync_interval_minutes
        ),
        job_id="sports_data_sync",
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
        scheduler.shutdown()

        logger.info(
            "Scheduler encerrado."
        )

        print(
            "Scheduler encerrado com sucesso."
        )


if __name__ == "__main__":
    main()