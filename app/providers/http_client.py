from __future__ import annotations

import logging
import time
from collections.abc import Mapping
from typing import Any

import httpx

from app.providers.exceptions import (
    ProviderDataError,
    ProviderNetworkError,
    ProviderRateLimitError,
    ProviderResponseError,
)
from app.providers.rate_limiter import (
    RateLimiter,
)


logger = logging.getLogger(
    "ultrastats.providers.http"
)


RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}


class ProviderHTTPClient:
    """
    Cliente HTTP reutilizável para APIs
    externas do UltraStats AI.
    """

    def __init__(
        self,
        *,
        base_url: str,
        default_headers: (
            Mapping[str, str] | None
        ) = None,
        timeout_seconds: float = 15.0,
        max_retries: int = 3,
        retry_delay_seconds: float = 1.0,
        requests_per_minute: (
            int | None
        ) = None,
        transport: (
            httpx.BaseTransport | None
        ) = None,
    ) -> None:
        normalized_base_url = (
            base_url.strip()
        )

        if not normalized_base_url:
            raise ValueError(
                "base_url não pode ser vazia."
            )

        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds deve ser "
                "maior que zero."
            )

        if max_retries < 0:
            raise ValueError(
                "max_retries não pode "
                "ser negativo."
            )

        if retry_delay_seconds < 0:
            raise ValueError(
                "retry_delay_seconds não pode "
                "ser negativo."
            )

        self.base_url = (
            normalized_base_url.rstrip("/")
        )

        self.timeout_seconds = (
            timeout_seconds
        )

        self.max_retries = (
            max_retries
        )

        self.retry_delay_seconds = (
            retry_delay_seconds
        )

        self.rate_limiter = (
            RateLimiter(
                requests_per_minute
            )
            if requests_per_minute
            is not None
            else None
        )

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=dict(
                default_headers or {}
            ),
            timeout=httpx.Timeout(
                timeout_seconds
            ),
            transport=transport,
            follow_redirects=True,
        )

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: (
            Mapping[str, Any] | None
        ) = None,
        headers: (
            Mapping[str, str] | None
        ) = None,
        json: Any = None,
    ) -> httpx.Response:
        """
        Realiza uma requisição HTTP com
        retry e controle de taxa.
        """

        normalized_method = (
            method.strip().upper()
        )

        if not normalized_method:
            raise ValueError(
                "O método HTTP não pode "
                "ser vazio."
            )

        normalized_endpoint = (
            endpoint.strip()
        )

        total_attempts = (
            self.max_retries
            + 1
        )

        for attempt_number in range(
            1,
            total_attempts + 1,
        ):
            if self.rate_limiter is not None:
                self.rate_limiter.acquire()

            logger.debug(
                "Requisição ao provider | "
                "método=%s | endpoint=%s | "
                "tentativa=%s/%s",
                normalized_method,
                normalized_endpoint,
                attempt_number,
                total_attempts,
            )

            try:
                response = self._client.request(
                    method=normalized_method,
                    url=normalized_endpoint,
                    params=params,
                    headers=headers,
                    json=json,
                )

            except httpx.TimeoutException as error:
                logger.warning(
                    "Timeout no provider | "
                    "endpoint=%s | "
                    "tentativa=%s/%s",
                    normalized_endpoint,
                    attempt_number,
                    total_attempts,
                )

                if attempt_number >= total_attempts:
                    raise ProviderNetworkError(
                        "O provedor excedeu o "
                        "tempo máximo de resposta."
                    ) from error

                self._sleep_before_retry(
                    attempt_number
                )

                continue

            except httpx.RequestError as error:
                logger.warning(
                    "Falha de rede no provider | "
                    "endpoint=%s | erro=%s | "
                    "tentativa=%s/%s",
                    normalized_endpoint,
                    error,
                    attempt_number,
                    total_attempts,
                )

                if attempt_number >= total_attempts:
                    raise ProviderNetworkError(
                        "Não foi possível acessar "
                        "o provedor externo."
                    ) from error

                self._sleep_before_retry(
                    attempt_number
                )

                continue

            if response.status_code < 400:
                logger.debug(
                    "Resposta recebida | "
                    "endpoint=%s | status=%s",
                    normalized_endpoint,
                    response.status_code,
                )

                return response

            if (
                response.status_code
                in RETRYABLE_STATUS_CODES
            ):
                logger.warning(
                    "Erro temporário do provider | "
                    "endpoint=%s | status=%s | "
                    "tentativa=%s/%s",
                    normalized_endpoint,
                    response.status_code,
                    attempt_number,
                    total_attempts,
                )

                if attempt_number < total_attempts:
                    self._sleep_before_retry(
                        attempt_number,
                        response=response,
                    )

                    continue

            self._raise_response_error(
                response
            )

        raise ProviderNetworkError(
            "A requisição foi encerrada "
            "sem uma resposta válida."
        )

    def get(
        self,
        endpoint: str,
        *,
        params: (
            Mapping[str, Any] | None
        ) = None,
        headers: (
            Mapping[str, str] | None
        ) = None,
    ) -> httpx.Response:
        return self.request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
        )

    def get_json(
        self,
        endpoint: str,
        *,
        params: (
            Mapping[str, Any] | None
        ) = None,
        headers: (
            Mapping[str, str] | None
        ) = None,
    ) -> Any:
        response = self.get(
            endpoint,
            params=params,
            headers=headers,
        )

        try:
            return response.json()

        except ValueError as error:
            logger.exception(
                "Resposta JSON inválida | "
                "endpoint=%s",
                endpoint,
            )

            raise ProviderDataError(
                "O provedor retornou um "
                "JSON inválido."
            ) from error

    def close(
        self,
    ) -> None:
        self._client.close()

    def __enter__(
        self,
    ) -> ProviderHTTPClient:
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        self.close()

    def _sleep_before_retry(
        self,
        attempt_number: int,
        *,
        response: (
            httpx.Response | None
        ) = None,
    ) -> None:
        retry_after_seconds = (
            self._get_retry_after_seconds(
                response
            )
        )

        if retry_after_seconds is None:
            retry_after_seconds = (
                self.retry_delay_seconds
                * attempt_number
            )

        if retry_after_seconds <= 0:
            return

        logger.debug(
            "Aguardando antes do retry | "
            "segundos=%.2f",
            retry_after_seconds,
        )

        time.sleep(
            retry_after_seconds
        )

    @staticmethod
    def _get_retry_after_seconds(
        response: (
            httpx.Response | None
        ),
    ) -> float | None:
        if response is None:
            return None

        retry_after = response.headers.get(
            "Retry-After"
        )

        if retry_after is None:
            return None

        try:
            return max(
                float(retry_after),
                0.0,
            )

        except ValueError:
            return None

    @staticmethod
    def _raise_response_error(
        response: httpx.Response,
    ) -> None:
        response_text = (
            response.text[:1000]
            if response.text
            else None
        )

        message = (
            "O provedor retornou erro HTTP "
            f"{response.status_code}."
        )

        error_arguments = {
            "status_code": (
                response.status_code
            ),
            "url": str(
                response.request.url
            ),
            "response_text": (
                response_text
            ),
        }

        if response.status_code == 429:
            raise ProviderRateLimitError(
                message,
                **error_arguments,
            )

        raise ProviderResponseError(
            message,
            **error_arguments,
        )