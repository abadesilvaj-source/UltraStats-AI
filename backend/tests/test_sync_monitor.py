from app.models import SyncRun


def test_sync_run_model() -> None:
    run = SyncRun(
        source="test_provider",
        status="started",
        triggered_by="test",
    )

    assert run.source == "test_provider"
    assert run.status == "started"
    assert run.triggered_by == "test"