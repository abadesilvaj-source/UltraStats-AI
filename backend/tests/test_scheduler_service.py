from app.scheduler.scheduler_service import (
    SchedulerService,
)
from datetime import datetime


def test_scheduler_can_add_job() -> None:
    scheduler = SchedulerService()

    def sample_job() -> None:
        pass

    scheduler.add_interval_job(
        func=sample_job,
        minutes=1,
        job_id="test_job",
    )

    jobs = scheduler.get_jobs()

    assert len(jobs) == 1
    assert jobs[0]["id"] == "test_job"


def test_scheduler_rejects_invalid_interval() -> None:
    scheduler = SchedulerService()

    def sample_job() -> None:
        pass

    try:
        scheduler.add_interval_job(
            func=sample_job,
            minutes=0,
            job_id="invalid_job",
        )

    except ValueError:
        assert True

    else:
        assert False


def test_immediate_job_uses_scheduler_timezone() -> None:
    scheduler = SchedulerService()
    scheduler.add_seconds_job(
        func=lambda: None,
        seconds=60,
        job_id="immediate",
        run_immediately=True,
    )
    next_run = scheduler.get_jobs()[0]["next_run_time"]
    assert next_run.tzinfo is not None
    assert next_run <= datetime.now(scheduler.scheduler.timezone)
