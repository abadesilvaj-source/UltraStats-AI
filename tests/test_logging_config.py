import logging
from pathlib import Path

from app.core.logging_config import (
    configure_logging,
)


def test_configure_logging_creates_handlers(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "log_directory",
        str(tmp_path),
    )

    monkeypatch.setattr(
        settings,
        "log_console_enabled",
        False,
    )

    monkeypatch.setattr(
        settings,
        "log_file_enabled",
        True,
    )

    root_logger = logging.getLogger()

    for handler in list(
        root_logger.handlers
    ):
        root_logger.removeHandler(
            handler
        )

        handler.close()

    if hasattr(
        root_logger,
        "_ultrastats_configured_service",
    ):
        delattr(
            root_logger,
            "_ultrastats_configured_service",
        )

    logger = configure_logging(
        "teste"
    )

    logger.info(
        "Mensagem de teste."
    )

    service_log = (
        tmp_path
        / "teste.log"
    )

    error_log = (
        tmp_path
        / "errors.log"
    )

    assert service_log.exists()
    assert error_log.exists()


def test_configure_logging_does_not_duplicate_handlers(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "log_directory",
        str(tmp_path),
    )

    monkeypatch.setattr(
        settings,
        "log_console_enabled",
        False,
    )

    monkeypatch.setattr(
        settings,
        "log_file_enabled",
        True,
    )

    root_logger = logging.getLogger()

    for handler in list(
        root_logger.handlers
    ):
        root_logger.removeHandler(
            handler
        )

        handler.close()

    if hasattr(
        root_logger,
        "_ultrastats_configured_service",
    ):
        delattr(
            root_logger,
            "_ultrastats_configured_service",
        )

    configure_logging(
        "dashboard"
    )

    first_handler_count = len(
        root_logger.handlers
    )

    configure_logging(
        "dashboard"
    )

    second_handler_count = len(
        root_logger.handlers
    )

    assert (
        first_handler_count
        == second_handler_count
    )


def test_errors_are_written_to_errors_log(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "log_directory",
        str(tmp_path),
    )

    monkeypatch.setattr(
        settings,
        "log_console_enabled",
        False,
    )

    monkeypatch.setattr(
        settings,
        "log_file_enabled",
        True,
    )

    root_logger = logging.getLogger()

    for handler in list(
        root_logger.handlers
    ):
        root_logger.removeHandler(
            handler
        )

        handler.close()

    if hasattr(
        root_logger,
        "_ultrastats_configured_service",
    ):
        delattr(
            root_logger,
            "_ultrastats_configured_service",
        )

    logger = configure_logging(
        "teste_erros"
    )

    logger.info(
        "Mensagem informativa."
    )

    logger.error(
        "Mensagem de erro."
    )

    for handler in root_logger.handlers:
        handler.flush()

    error_log = (
        tmp_path
        / "errors.log"
    )

    content = error_log.read_text(
        encoding="utf-8"
    )

    assert "Mensagem de erro." in content
    assert "Mensagem informativa." not in content