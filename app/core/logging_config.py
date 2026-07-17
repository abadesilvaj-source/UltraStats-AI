from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


DEFAULT_LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)

DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _get_log_level() -> int:
    """
    Converte o nível definido no ambiente
    para um nível válido do módulo logging.
    """

    level_name = str(
        settings.log_level
    ).strip().upper()

    level = getattr(
        logging,
        level_name,
        None,
    )

    if not isinstance(level, int):
        return logging.INFO

    return level


def _create_formatter() -> logging.Formatter:
    """
    Cria o formato padronizado usado por
    todos os logs do UltraStats AI.
    """

    return logging.Formatter(
        fmt=DEFAULT_LOG_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
    )


def _create_console_handler(
    formatter: logging.Formatter,
) -> logging.Handler:
    """
    Cria o handler responsável por imprimir
    logs no terminal e no Docker.
    """

    handler = logging.StreamHandler(
        stream=sys.stdout
    )

    handler.setLevel(
        _get_log_level()
    )

    handler.setFormatter(
        formatter
    )

    handler._ultrastats_handler_type = (
        "console"
    )

    return handler


def _create_rotating_file_handler(
    file_path: Path,
    formatter: logging.Formatter,
    level: int,
) -> RotatingFileHandler:
    """
    Cria um arquivo de log com rotação
    automática por tamanho.
    """

    handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )

    handler.setLevel(
        level
    )

    handler.setFormatter(
        formatter
    )

    handler._ultrastats_handler_type = (
        "rotating_file"
    )

    handler._ultrastats_file_path = str(
        file_path
    )

    return handler

def _add_module_file_handler(
    logger_name: str,
    file_name: str,
    formatter: logging.Formatter,
    level: int,
) -> None:
    """
    Adiciona um arquivo exclusivo para
    um logger específico da aplicação.
    """

    if not settings.log_file_enabled:
        return

    module_logger = logging.getLogger(
        logger_name
    )

    for handler in module_logger.handlers:
        if getattr(
            handler,
            "_ultrastats_file_name",
            None,
        ) == file_name:
            return

    log_directory = Path(
        settings.log_directory
    )

    log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    handler = _create_rotating_file_handler(
        file_path=(
            log_directory
            / file_name
        ),
        formatter=formatter,
        level=level,
    )

    handler._ultrastats_file_name = (
        file_name
    )

    module_logger.addHandler(
        handler
    )

    module_logger.setLevel(
        level
    )

    module_logger.propagate = True

def configure_logging(
    service_name: str = "ultrastats",
) -> logging.Logger:
    """
    Configura os logs de um serviço.

    Exemplos:
        configure_logging("scheduler")
        configure_logging("dashboard")
        configure_logging("collectors")
    """

    normalized_service_name = (
        service_name
        .strip()
        .lower()
        .replace(" ", "_")
    )

    if not normalized_service_name:
        normalized_service_name = "ultrastats"

    # Obtém o logger raiz antes de qualquer uso.
    root_logger = logging.getLogger()

    configured_service = getattr(
        root_logger,
        "_ultrastats_configured_service",
        None,
    )

    # Impede a duplicação de handlers em reruns
    # do Streamlit.
    if (
        configured_service
        == normalized_service_name
        and root_logger.handlers
    ):
        return logging.getLogger(
            f"ultrastats.{normalized_service_name}"
        )

    log_level = _get_log_level()
    formatter = _create_formatter()

    root_logger.setLevel(
        log_level
    )

    # Remove handlers anteriores para evitar
    # mensagens duplicadas.
    for existing_handler in list(
        root_logger.handlers
    ):
        root_logger.removeHandler(
            existing_handler
        )

        try:
            existing_handler.close()
        except Exception:
            pass

    if settings.log_console_enabled:
        root_logger.addHandler(
            _create_console_handler(
                formatter
            )
        )

    if settings.log_file_enabled:
        log_directory = Path(
            settings.log_directory
        )

        log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        service_log_path = (
            log_directory
            / f"{normalized_service_name}.log"
        )

        error_log_path = (
            log_directory
            / "errors.log"
        )

        service_handler = (
            _create_rotating_file_handler(
                file_path=service_log_path,
                formatter=formatter,
                level=log_level,
            )
        )

        error_handler = (
            _create_rotating_file_handler(
                file_path=error_log_path,
                formatter=formatter,
                level=logging.ERROR,
            )
        )

        root_logger.addHandler(
            service_handler
        )

        root_logger.addHandler(
            error_handler
        )

        _add_module_file_handler(
            logger_name="ultrastats.collectors",
            file_name="collectors.log",
            formatter=formatter,
            level=log_level,
        )

    # Reduz mensagens excessivas de bibliotecas.
    logging.getLogger(
        "sqlalchemy.engine"
    ).setLevel(
        logging.WARNING
    )

    logging.getLogger(
        "apscheduler"
    ).setLevel(
        logging.INFO
    )

    logging.getLogger(
        "urllib3"
    ).setLevel(
        logging.WARNING
    )

    logging.getLogger(
        "httpx"
    ).setLevel(
        logging.WARNING
    )

    logger = logging.getLogger(
        f"ultrastats.{normalized_service_name}"
    )

    root_logger._ultrastats_configured_service = (
        normalized_service_name
    )

    logger.info(
        "Sistema de logs configurado | "
        "serviço=%s | nível=%s | diretório=%s",
        normalized_service_name,
        logging.getLevelName(
            log_level
        ),
        settings.log_directory,
    )

    return logger

def configure_collector_logging() -> logging.Logger:
    """
    Mantém compatibilidade com os módulos
    antigos que ainda chamam essa função.
    """

    return configure_logging(
        service_name="collectors"
    )

def get_logging_status() -> dict:
    """
    Retorna informações sobre os handlers
    atualmente configurados.
    """

    root_logger = logging.getLogger()

    handlers = []

    for handler in root_logger.handlers:
        handlers.append(
            {
                "type": getattr(
                    handler,
                    "_ultrastats_handler_type",
                    handler.__class__.__name__,
                ),
                "level": logging.getLevelName(
                    handler.level
                ),
                "file_path": getattr(
                    handler,
                    "_ultrastats_file_path",
                    None,
                ),
            }
        )

    return {
        "root_level": logging.getLevelName(
            root_logger.level
        ),
        "configured_service": getattr(
            root_logger,
            "_ultrastats_configured_service",
            None,
        ),
        "handler_count": len(
            root_logger.handlers
        ),
        "handlers": handlers,
    }