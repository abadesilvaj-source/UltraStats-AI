import logging
import threading
import time
from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.config import settings
from app.core.logging_config import (
    configure_logging,
)

from app.database.session import SessionLocal
from app.models import SyncRun
from app.scheduler import (
    SchedulerService,
    run_scheduled_live_sync,
    run_scheduled_backfill,
    run_scheduled_odds_sync,
    run_scheduled_paper_trading,
    run_scheduled_model_training,
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


def initial_sync_is_due() -> bool:
    """Evita consumir franquia externa novamente em todo restart."""
    session = SessionLocal()
    try:
        latest = session.scalar(
            select(SyncRun)
            .where(SyncRun.source == "multi_provider")
            .order_by(SyncRun.started_at.desc())
        )
        if latest is None:
            return True
        reference = latest.finished_at or latest.started_at
        if reference is None:
            return True
        # Um restart durante indisponibilidade de rede não deve iniciar uma
        # tempestade de sincronizações completas. A tentativa recente conta
        # como ciclo para fins de espaçamento, mesmo quando falhou ou foi
        # interrompida.
        return reference <= (
            datetime.now()
            - timedelta(minutes=settings.sync_interval_minutes)
        )
    finally:
        session.close()

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
        run_immediately=initial_sync_is_due(),
    )

    # Coleta leve e independente para API-Football/Sportmonks.
    scheduler.add_seconds_job(
        func=run_scheduled_live_sync,
        seconds=settings.live_sync_interval_seconds,
        job_id="live_scores_sync",
        run_immediately=False,
    )

    if settings.backfill_enabled:
        scheduler.add_interval_job(
            func=run_scheduled_backfill,
            minutes=settings.backfill_interval_minutes,
            job_id="statistics_backfill",
            run_immediately=False,
        )

    if settings.odds_sync_enabled:
        scheduler.add_interval_job(
            func=run_scheduled_odds_sync,
            minutes=settings.odds_sync_interval_minutes,
            job_id="odds_refresh",
            run_immediately=False,
        )

    if settings.paper_trading_enabled:
        scheduler.add_interval_job(
            func=run_scheduled_paper_trading,
            minutes=settings.paper_trading_interval_minutes,
            job_id="automatic_paper_trading",
            run_immediately=False,
        )

    scheduler.add_interval_job(
        func=run_scheduled_model_training,
        minutes=5,
        job_id="dedicated_model_training",
        run_immediately=False,
    )

    scheduler.start()

    logger.info(
        "Scheduler iniciado | "
        "instância=%s | "
        "provedor=%s | "
        "intervalo_sync=%s minuto(s) | intervalo_live=%s segundo(s) | "
        "intervalo_backfill=%s minuto(s) | intervalo_odds=%s minuto(s) | "
        "intervalo_heartbeat=%s segundo(s)",
        settings.scheduler_instance_name,
        settings.sync_provider,
        settings.sync_interval_minutes,
        settings.live_sync_interval_seconds,
        settings.backfill_interval_minutes,
        settings.odds_sync_interval_minutes,
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
