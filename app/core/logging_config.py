import logging
from pathlib import Path


def configure_collector_logging() -> None:
    logs_directory = Path(
        "logs"
    )

    logs_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = logging.getLogger(
        "ultrastats.collectors"
    )

    if logger.handlers:
        return

    logger.setLevel(
        logging.INFO
    )

    formatter = logging.Formatter(
        (
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        )
    )

    file_handler = logging.FileHandler(
        logs_directory
        / "collectors.log",
        encoding="utf-8",
    )

    file_handler.setFormatter(
        formatter
    )

    console_handler = (
        logging.StreamHandler()
    )

    console_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )