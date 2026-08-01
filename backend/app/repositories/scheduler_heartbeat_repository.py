from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SchedulerHeartbeat


class SchedulerHeartbeatRepository:
    """
    Operações de banco relacionadas
    ao heartbeat do scheduler.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def create(
        self,
        heartbeat: SchedulerHeartbeat,
    ) -> SchedulerHeartbeat:
        self.session.add(
            heartbeat
        )

        self.session.flush()

        return heartbeat

    def update(
        self,
        heartbeat: SchedulerHeartbeat,
    ) -> SchedulerHeartbeat:
        self.session.flush()

        return heartbeat

    def find_by_instance_name(
        self,
        instance_name: str,
    ) -> SchedulerHeartbeat | None:
        statement = select(
            SchedulerHeartbeat
        ).where(
            SchedulerHeartbeat.instance_name
            == instance_name
        )

        return self.session.scalar(
            statement
        )

    def list_all(
        self,
    ) -> list[SchedulerHeartbeat]:
        statement = (
            select(SchedulerHeartbeat)
            .order_by(
                SchedulerHeartbeat
                .last_heartbeat_at
                .desc()
            )
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )