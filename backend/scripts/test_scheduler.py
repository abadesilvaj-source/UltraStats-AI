import time

from app.scheduler.jobs import (
    scheduler_heartbeat,
)

from app.scheduler.scheduler_service import (
    SchedulerService,
)


scheduler = SchedulerService()

scheduler.add_interval_job(
    scheduler_heartbeat,
    minutes=1,
    job_id="heartbeat",
)

scheduler.start()

print("Scheduler iniciado.")

try:

    while True:

        time.sleep(1)

except KeyboardInterrupt:

    scheduler.shutdown()

    print("Scheduler encerrado.")