import sys
from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.config import settings
from app.database.session import SessionLocal
from app.models import SchedulerHeartbeat


def main() -> None:
    session = SessionLocal()

    try:
        heartbeat = session.scalar(
            select(SchedulerHeartbeat).where(
                SchedulerHeartbeat.instance_name
                == settings.scheduler_instance_name
            )
        )

        if heartbeat is None:
            print(
                "Heartbeat do scheduler não encontrado."
            )
            sys.exit(1)

        offline_limit = (
            datetime.now()
            - timedelta(
                seconds=(
                    settings
                    .scheduler_offline_after_seconds
                )
            )
        )

        is_healthy = (
            heartbeat.active
            and heartbeat.status == "online"
            and heartbeat.last_heartbeat_at
            >= offline_limit
        )

        if not is_healthy:
            print(
                "Scheduler sem heartbeat recente."
            )
            sys.exit(1)

        print(
            "Scheduler saudável."
        )

    except Exception as error:
        print(
            f"Falha no healthcheck: {error}"
        )
        sys.exit(1)

    finally:
        session.close()


if __name__ == "__main__":
    main()