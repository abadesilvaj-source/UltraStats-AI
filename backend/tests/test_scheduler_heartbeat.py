from datetime import datetime, timedelta

from app.models import SchedulerHeartbeat


def test_scheduler_heartbeat_model() -> None:
    heartbeat = SchedulerHeartbeat(
        instance_name="test-instance",
        status="online",
        active=True,
        started_at=datetime.now(),
        last_heartbeat_at=datetime.now(),
    )

    assert heartbeat.instance_name == (
        "test-instance"
    )

    assert heartbeat.status == "online"
    assert heartbeat.active is True


def test_old_heartbeat_date() -> None:
    old_date = (
        datetime.now()
        - timedelta(minutes=5)
    )

    heartbeat = SchedulerHeartbeat(
        instance_name="old-instance",
        status="online",
        active=True,
        started_at=old_date,
        last_heartbeat_at=old_date,
    )

    assert heartbeat.last_heartbeat_at < (
        datetime.now()
    )