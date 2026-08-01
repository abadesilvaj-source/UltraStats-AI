import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def parse_bool(
    value: str | None,
    default: bool = False,
) -> bool:
    """
    Converte valores de texto do .env para booleano.

    Exemplos considerados verdadeiros:
    true, 1, yes, sim, on
    """

    if value is None:
        return default

    return value.strip().lower() in {
        "true",
        "1",
        "yes",
        "sim",
        "on",
    }


class Settings:
    """Configurações gerais do UltraStats AI."""

    def __init__(self) -> None:
        # Configurações gerais
        self.app_name = "UltraStats AI"
        self.version = "0.1.0"

        # Banco de dados
        self.database_url = os.getenv(
            "DATABASE_URL",
            "",
        )

        # Scheduler
        self.sync_enabled = parse_bool(
            os.getenv("SYNC_ENABLED"),
            default=True,
        )

        self.sync_interval_minutes = int(
            os.getenv(
                "SYNC_INTERVAL_MINUTES",
                "60",
            )
        )

        self.live_sync_interval_minutes = int(
            os.getenv(
                "LIVE_SYNC_INTERVAL_MINUTES",
                "30",
            )
        )
        self.live_sync_interval_seconds = int(
            os.getenv(
                "LIVE_SYNC_INTERVAL_SECONDS",
                str(self.live_sync_interval_minutes * 60),
            )
        )

        # Workers de enriquecimento independentes. Eles evitam que um
        # backfill demorado atrase placares, escalações e o ciclo principal.
        self.backfill_enabled = parse_bool(
            os.getenv("BACKFILL_ENABLED"), default=True
        )
        self.backfill_interval_minutes = int(
            os.getenv("BACKFILL_INTERVAL_MINUTES", "10")
        )
        self.odds_sync_enabled = parse_bool(
            os.getenv("ODDS_SYNC_ENABLED"), default=True
        )
        self.odds_sync_interval_minutes = int(
            os.getenv("ODDS_SYNC_INTERVAL_MINUTES", "15")
        )

        self.sync_provider = os.getenv(
            "SYNC_PROVIDER",
            "mock_provider",
        ).strip()

        self.sync_max_runtime_minutes = int(
            os.getenv(
                "SYNC_MAX_RUNTIME_MINUTES",
                "20",
            )
        )

        self.scheduler_heartbeat_seconds = int(
            os.getenv(
                "SCHEDULER_HEARTBEAT_SECONDS",
                "30",
            )
        )

        self.scheduler_offline_after_seconds = int(
            os.getenv(
                "SCHEDULER_OFFLINE_AFTER_SECONDS",
                "90",
            )
        )

        self.scheduler_instance_name = os.getenv(
            "SCHEDULER_INSTANCE_NAME",
            "ultrastats-main",
        ).strip()

        # Validações
        if self.sync_interval_minutes <= 0:
            raise ValueError(
                "SYNC_INTERVAL_MINUTES deve ser maior que zero."
            )

        if self.live_sync_interval_minutes <= 0:
            raise ValueError(
                "LIVE_SYNC_INTERVAL_MINUTES deve ser maior que zero."
            )
        if self.live_sync_interval_seconds < 30:
            raise ValueError(
                "LIVE_SYNC_INTERVAL_SECONDS deve ser no mínimo 30."
            )
        if self.backfill_interval_minutes <= 0:
            raise ValueError(
                "BACKFILL_INTERVAL_MINUTES deve ser maior que zero."
            )
        if self.odds_sync_interval_minutes <= 0:
            raise ValueError(
                "ODDS_SYNC_INTERVAL_MINUTES deve ser maior que zero."
            )

        if self.sync_max_runtime_minutes <= 0:
            raise ValueError(
                "SYNC_MAX_RUNTIME_MINUTES deve ser maior que zero."
            )

        if not self.sync_provider:
            raise ValueError(
                "SYNC_PROVIDER não pode ficar vazio."
            )
        
        if self.scheduler_heartbeat_seconds <= 0:
            raise ValueError(
                "SCHEDULER_HEARTBEAT_SECONDS "
                "deve ser maior que zero."
            )

        if self.scheduler_offline_after_seconds <= 0:
            raise ValueError(
                "SCHEDULER_OFFLINE_AFTER_SECONDS "
                "deve ser maior que zero."
            )

        if (
            self.scheduler_offline_after_seconds
            <= self.scheduler_heartbeat_seconds
        ):
            raise ValueError(
                "SCHEDULER_OFFLINE_AFTER_SECONDS "
                "deve ser maior que "
                "SCHEDULER_HEARTBEAT_SECONDS."
            )

        if not self.scheduler_instance_name:
            raise ValueError(
                "SCHEDULER_INSTANCE_NAME "
                "não pode ficar vazio."
            )
    # Logging
    log_level: str = "INFO"
    log_directory: str = "logs"
    log_max_bytes: int = 5_000_000
    log_backup_count: int = 5
    log_console_enabled: bool = True
    log_file_enabled: bool = True        
    
    # Providers
    provider_name: str = "mock"
    provider_http_timeout_seconds: float = 15.0
    provider_http_max_retries: int = 3
    provider_http_retry_delay_seconds: float = 1.0
    provider_default_requests_per_minute: int = 10
    provider_user_agent: str = (
        "UltraStats-AI/1.0"
    )

settings = Settings()
