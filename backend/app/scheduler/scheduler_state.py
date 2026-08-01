from dataclasses import dataclass
from datetime import datetime
from threading import Lock


@dataclass
class SchedulerRuntimeState:
    """
    Mantém informações do scheduler
    durante a execução atual do processo.
    """

    running: bool = False
    current_job_running: bool = False

    started_at: datetime | None = None
    last_job_started_at: datetime | None = None
    last_job_finished_at: datetime | None = None

    last_job_status: str | None = None
    last_error: str | None = None


scheduler_state = SchedulerRuntimeState()

scheduler_lock = Lock()