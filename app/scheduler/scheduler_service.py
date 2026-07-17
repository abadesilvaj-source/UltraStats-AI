from collections.abc import Callable

from apscheduler.schedulers.background import (
    BackgroundScheduler,
)

from app.scheduler.scheduler_state import (
    scheduler_state,
)


class SchedulerService:
    """
    Controla o APScheduler do UltraStats AI.
    """

    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler(
            timezone="America/Sao_Paulo"
        )

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

            scheduler_state.running = True

            from datetime import datetime

            scheduler_state.started_at = (
                datetime.now()
            )

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(
                wait=True
            )

        scheduler_state.running = False

    def add_interval_job(
        self,
        func: Callable,
        minutes: int,
        job_id: str,
        run_immediately: bool = False,
    ) -> None:
        if minutes <= 0:
            raise ValueError(
                "O intervalo deve ser maior que zero."
            )

        job_kwargs = {
            "func": func,
            "trigger": "interval",
            "minutes": minutes,
            "id": job_id,
            "replace_existing": True,
            "max_instances": 1,
            "coalesce": True,
            "misfire_grace_time": 300,
        }

        if run_immediately:
            from datetime import datetime

            job_kwargs["next_run_time"] = (
                datetime.now()
            )

        self.scheduler.add_job(
            **job_kwargs
        )

    def add_seconds_job(
        self,
        func: Callable,
        seconds: int,
        job_id: str,
        run_immediately: bool = False,
    ) -> None:
        if seconds <= 0:
            raise ValueError(
                "O intervalo em segundos "
                "deve ser maior que zero."
            )

        job_kwargs = {
            "func": func,
            "trigger": "interval",
            "seconds": seconds,
            "id": job_id,
            "replace_existing": True,
            "max_instances": 1,
            "coalesce": True,
            "misfire_grace_time": 30,
        }

        if run_immediately:
            from datetime import datetime

            job_kwargs["next_run_time"] = (
                datetime.now()
            )

        self.scheduler.add_job(
            **job_kwargs
        )

    def get_jobs(
        self,
    ) -> list[dict]:
        jobs = self.scheduler.get_jobs()

        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": getattr(
                    job,
                    "next_run_time",
                    None,
                ),
            }
            for job in jobs
        ]   