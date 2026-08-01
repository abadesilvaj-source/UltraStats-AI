from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import SyncRun
from app.services.sync_monitor_service import SyncMonitorService


def test_new_cycle_closes_orphaned_execution_from_same_source():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        monitor = SyncMonitorService(session)
        first = monitor.start_run("multi_provider_odds", "scheduler")
        second = monitor.start_run("multi_provider_odds", "scheduler")

        rows = session.scalars(
            select(SyncRun).order_by(SyncRun.id)
        ).all()
        assert first.id != second.id
        assert rows[0].status == "failed"
        assert rows[0].finished_at is not None
        assert "interrompida" in rows[0].error_message
        assert rows[1].status == "started"
