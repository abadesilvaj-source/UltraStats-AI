import os

from dotenv import load_dotenv


load_dotenv()


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


settings = Settings()