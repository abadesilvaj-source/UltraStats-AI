import logging
import time
from typing import Any

import httpx

from app.collectors.exceptions import (
    CollectorAuthenticationError,
    CollectorConnectionError,
    CollectorRateLimitError,
    CollectorResponseError,
)
from app.core.collector_settings import (
    CollectorSettings,
)


logger = logging.getLogger(
    "ultrastats.collectors.http"
)


class SportsHttpClient:
    """
    Cliente HTTP reutilizável para provedores esportivos.

    Possui:

    - timeout;
    - retry;
    - tratamento de rate limit;
    - tratamento de autenticação;
    - logs;
    - injeção de transporte para testes.
    """

    def __init__(
        self,
        settings: CollectorSettings,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.settings = settings

        headers = {
            "Accept": "application/json",
            "User-Agent": (
                "UltraStatsAI/0.1"
            ),
        }

        if settings.api_key:
            headers["Authorization"] = (
                f"Bearer {settings.api_key}"
            )

        self.client = httpx.Client(
            base_url=settings.base_url,
            headers=headers,
            timeout=settings.timeout,
            transport=transport,
        )

    def close(self) -> None:
        self.client.close()

    def __enter__(
        self,
    ) -> "SportsHttpClient":
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        self.close()

    def get_json(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict | list:
        """
        Realiza uma requisição GET e devolve JSON.
        """

        normalized_endpoint = (
            endpoint
            if endpoint.startswith("/")
            else f"/{endpoint}"
        )

        last_error: Exception | None = None

        total_attempts = (
            self.settings.max_retries + 1
        )

        for attempt in range(
            1,
            total_attempts + 1,
        ):
            try:
                logger.info(
                    "GET %s | tentativa %s/%s",
                    normalized_endpoint,
                    attempt,
                    total_attempts,
                )

                response = self.client.get(
                    normalized_endpoint,
                    params=params,
                )

                if response.status_code in {
                    401,
                    403,
                }:
                    raise CollectorAuthenticationError(
                        "A API rejeitou as credenciais."
                    )

                if response.status_code == 429:
                    retry_after = response.headers.get(
                        "Retry-After"
                    )

                    if retry_after:
                        wait_seconds = float(
                            retry_after
                        )
                    else:
                        wait_seconds = (
                            self.settings.retry_delay
                            * attempt
                        )

                    last_error = (
                        CollectorRateLimitError(
                            "Limite de requisições atingido."
                        )
                    )

                    if attempt < total_attempts:
                        logger.warning(
                            "Rate limit. Nova tentativa "
                            "em %.2f segundos.",
                            wait_seconds,
                        )

                        time.sleep(
                            wait_seconds
                        )

                        continue

                    raise last_error

                if response.status_code >= 500:
                    last_error = (
                        CollectorResponseError(
                            "O servidor do provedor "
                            f"retornou HTTP "
                            f"{response.status_code}."
                        )
                    )

                    if attempt < total_attempts:
                        wait_seconds = (
                            self.settings.retry_delay
                            * attempt
                        )

                        logger.warning(
                            "Erro temporário HTTP %s. "
                            "Nova tentativa em %.2f segundos.",
                            response.status_code,
                            wait_seconds,
                        )

                        time.sleep(
                            wait_seconds
                        )

                        continue

                    raise last_error

                if response.status_code >= 400:
                    raise CollectorResponseError(
                        "O provedor retornou erro "
                        f"HTTP {response.status_code}: "
                        f"{response.text[:300]}"
                    )

                try:
                    payload = response.json()

                except ValueError as error:
                    raise CollectorResponseError(
                        "O provedor não retornou "
                        "um JSON válido."
                    ) from error

                if not isinstance(
                    payload,
                    (dict, list),
                ):
                    raise CollectorResponseError(
                        "A resposta JSON possui "
                        "um formato inesperado."
                    )

                return payload

            except httpx.TimeoutException as error:
                last_error = (
                    CollectorConnectionError(
                        "A requisição excedeu "
                        "o tempo limite."
                    )
                )

                if attempt < total_attempts:
                    wait_seconds = (
                        self.settings.retry_delay
                        * attempt
                    )

                    logger.warning(
                        "Timeout. Nova tentativa "
                        "em %.2f segundos.",
                        wait_seconds,
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue

                raise last_error from error

            except httpx.RequestError as error:
                last_error = (
                    CollectorConnectionError(
                        "Não foi possível conectar "
                        "ao provedor."
                    )
                )

                if attempt < total_attempts:
                    wait_seconds = (
                        self.settings.retry_delay
                        * attempt
                    )

                    logger.warning(
                        "Erro de conexão. Nova tentativa "
                        "em %.2f segundos.",
                        wait_seconds,
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue

                raise last_error from error

        if last_error:
            raise last_error

        raise CollectorResponseError(
            "A requisição não pôde ser concluída."
        )