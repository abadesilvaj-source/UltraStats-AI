from apscheduler.schedulers.background import BackgroundScheduler


class SchedulerService:

    def __init__(self):

        self.scheduler = BackgroundScheduler()

    def start(self):

        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self):

        if self.scheduler.running:
            self.scheduler.shutdown()

    def add_interval_job(
        self,
        func,
        minutes,
        job_id,
    ):

        self.scheduler.add_job(
            func,
            trigger="interval",
            minutes=minutes,
            id=job_id,
            replace_existing=True,
        )