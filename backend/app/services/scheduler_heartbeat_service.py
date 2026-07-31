import os
import socket
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import SchedulerHeartbeat
from app.repositories import (
    SchedulerHeartbeatRepository,
)


class SchedulerHeartbeatService:
    """
    Gerencia o estado persistente
    do scheduler no PostgreSQL.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

        self.repository = (
            SchedulerHeartbeatRepository(
                session
            )
        )

    def register_start(
        self,
        instance_name: str,
        provider: str,
    ) -> SchedulerHeartbeat:
        now = datetime.now()

        heartbeat = (
            self.repository
            .find_by_instance_name(
                instance_name
            )
        )

        if heartbeat is None:
            heartbeat = SchedulerHeartbeat(
                instance_name=instance_name,
                status="online",
                active=True,
                process_id=os.getpid(),
                hostname=socket.gethostname(),
                provider=provider,
                started_at=now,
                last_heartbeat_at=now,
                stopped_at=None,
                last_job_status=None,
                last_job_started_at=None,
                last_job_finished_at=None,
                last_error=None,
            )

            self.repository.create(
                heartbeat
            )

        else:
            heartbeat.status = "online"
            heartbeat.active = True
            heartbeat.process_id = os.getpid()
            heartbeat.hostname = socket.gethostname()
            heartbeat.provider = provider
            heartbeat.started_at = now
            heartbeat.last_heartbeat_at = now
            heartbeat.stopped_at = None
            heartbeat.last_error = None

            self.repository.update(
                heartbeat
            )

        self.session.commit()
        self.session.refresh(heartbeat)

        return heartbeat

    def register_heartbeat(
        self,
        instance_name: str,
    ) -> SchedulerHeartbeat:
        heartbeat = (
            self.repository
            .find_by_instance_name(
                instance_name
            )
        )

        if heartbeat is None:
            raise ValueError(
                "Instância do scheduler não registrada."
            )

        heartbeat.status = "online"
        heartbeat.active = True
        heartbeat.last_heartbeat_at = datetime.now()

        self.repository.update(
            heartbeat
        )

        self.session.commit()
        self.session.refresh(heartbeat)

        return heartbeat

    def register_job_started(
        self,
        instance_name: str,
    ) -> SchedulerHeartbeat:
        heartbeat = self._get_required(
            instance_name
        )

        heartbeat.last_job_status = "running"
        heartbeat.last_job_started_at = datetime.now()
        heartbeat.last_error = None

        self.repository.update(
            heartbeat
        )

        self.session.commit()

        return heartbeat

    def register_job_finished(
        self,
        instance_name: str,
        status: str,
        error: str | None = None,
    ) -> SchedulerHeartbeat:
        heartbeat = self._get_required(
            instance_name
        )

        heartbeat.last_job_status = status
        heartbeat.last_job_finished_at = (
            datetime.now()
        )

        heartbeat.last_error = (
            error[:2000]
            if error
            else None
        )

        heartbeat.last_heartbeat_at = (
            datetime.now()
        )

        self.repository.update(
            heartbeat
        )

        self.session.commit()

        return heartbeat

    def register_stop(
        self,
        instance_name: str,
    ) -> SchedulerHeartbeat:
        heartbeat = self._get_required(
            instance_name
        )

        now = datetime.now()

        heartbeat.status = "stopped"
        heartbeat.active = False
        heartbeat.stopped_at = now
        heartbeat.last_heartbeat_at = now

        self.repository.update(
            heartbeat
        )

        self.session.commit()

        return heartbeat

    def get_status(
        self,
        instance_name: str,
    ) -> dict:
        heartbeat = (
            self.repository
            .find_by_instance_name(
                instance_name
            )
        )

        if heartbeat is None:
            return {
                "registered": False,
                "online": False,
                "status": "not_registered",
                "instance_name": instance_name,
            }

        now = datetime.now()

        offline_limit = (
            now
            - timedelta(
                seconds=(
                    settings
                    .scheduler_offline_after_seconds
                )
            )
        )

        online = (
            heartbeat.active
            and heartbeat.status == "online"
            and heartbeat.last_heartbeat_at
            >= offline_limit
        )

        seconds_since_heartbeat = (
            now
            - heartbeat.last_heartbeat_at
        ).total_seconds()

        return {
            "registered": True,
            "online": online,
            "status": (
                "online"
                if online
                else "offline"
            ),
            "instance_name": (
                heartbeat.instance_name
            ),
            "process_id": heartbeat.process_id,
            "hostname": heartbeat.hostname,
            "provider": heartbeat.provider,
            "started_at": heartbeat.started_at,
            "last_heartbeat_at": (
                heartbeat.last_heartbeat_at
            ),
            "seconds_since_heartbeat": (
                seconds_since_heartbeat
            ),
            "last_job_status": (
                heartbeat.last_job_status
            ),
            "last_job_started_at": (
                heartbeat.last_job_started_at
            ),
            "last_job_finished_at": (
                heartbeat.last_job_finished_at
            ),
            "last_error": heartbeat.last_error,
        }

    def _get_required(
        self,
        instance_name: str,
    ) -> SchedulerHeartbeat:
        heartbeat = (
            self.repository
            .find_by_instance_name(
                instance_name
            )
        )

        if heartbeat is None:
            raise ValueError(
                "Instância do scheduler não registrada."
            )

        return heartbeat