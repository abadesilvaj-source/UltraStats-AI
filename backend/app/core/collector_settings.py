import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def parse_bool(
    value: str | None,
    default: bool = False,
) -> bool:
    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "sim",
        "on",
    }


@dataclass(frozen=True)
class CollectorSettings:
    base_url: str
    api_key: str
    timeout: float
    max_retries: int
    retry_delay: float
    sandbox: bool


def get_collector_settings() -> CollectorSettings:
    base_url = os.getenv(
        "SPORTS_API_BASE_URL",
        "",
    ).strip()

    api_key = os.getenv(
        "SPORTS_API_KEY",
        "",
    ).strip()

    timeout = float(
        os.getenv(
            "SPORTS_API_TIMEOUT",
            "15",
        )
    )

    max_retries = int(
        os.getenv(
            "SPORTS_API_MAX_RETRIES",
            "3",
        )
    )

    retry_delay = float(
        os.getenv(
            "SPORTS_API_RETRY_DELAY",
            "1",
        )
    )

    sandbox = parse_bool(
        os.getenv(
            "SPORTS_API_SANDBOX"
        ),
        default=True,
    )

    if not base_url:
        raise ValueError(
            "SPORTS_API_BASE_URL não foi configurada."
        )

    if timeout <= 0:
        raise ValueError(
            "SPORTS_API_TIMEOUT deve ser positivo."
        )

    if max_retries < 0:
        raise ValueError(
            "SPORTS_API_MAX_RETRIES não pode ser negativo."
        )

    if retry_delay < 0:
        raise ValueError(
            "SPORTS_API_RETRY_DELAY não pode ser negativo."
        )

    return CollectorSettings(
        base_url=base_url.rstrip("/"),
        api_key=api_key,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay,
        sandbox=sandbox,
    )
