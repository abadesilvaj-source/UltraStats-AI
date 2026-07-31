import httpx
import pytest

from app.providers import (
    ProviderDataError,
    ProviderHTTPClient,
    ProviderRateLimitError,
    ProviderResponseError,
)


def test_get_json_returns_payload() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "status": "ok",
                "items": 3,
            },
            request=request,
        )

    transport = httpx.MockTransport(
        handler
    )

    with ProviderHTTPClient(
        base_url="https://provider.test",
        max_retries=0,
        transport=transport,
    ) as client:
        result = client.get_json(
            "/data"
        )

    assert result == {
        "status": "ok",
        "items": 3,
    }


def test_client_raises_response_error() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=401,
            json={
                "error": "unauthorized",
            },
            request=request,
        )

    transport = httpx.MockTransport(
        handler
    )

    with ProviderHTTPClient(
        base_url="https://provider.test",
        max_retries=0,
        transport=transport,
    ) as client:
        with pytest.raises(
            ProviderResponseError
        ) as error_info:
            client.get(
                "/protected"
            )

    assert (
        error_info.value.status_code
        == 401
    )


def test_client_retries_temporary_error() -> None:
    request_count = 0

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count

        request_count += 1

        if request_count < 3:
            return httpx.Response(
                status_code=503,
                request=request,
            )

        return httpx.Response(
            status_code=200,
            json={
                "status": "recovered",
            },
            request=request,
        )

    transport = httpx.MockTransport(
        handler
    )

    with ProviderHTTPClient(
        base_url="https://provider.test",
        max_retries=2,
        retry_delay_seconds=0,
        transport=transport,
    ) as client:
        result = client.get_json(
            "/unstable"
        )

    assert request_count == 3
    assert result == {
        "status": "recovered",
    }


def test_client_raises_rate_limit_error() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=429,
            headers={
                "Retry-After": "0",
            },
            request=request,
        )

    transport = httpx.MockTransport(
        handler
    )

    with ProviderHTTPClient(
        base_url="https://provider.test",
        max_retries=0,
        transport=transport,
    ) as client:
        with pytest.raises(
            ProviderRateLimitError
        ):
            client.get(
                "/limited"
            )


def test_get_json_rejects_invalid_json() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            content=b"not-json",
            request=request,
        )

    transport = httpx.MockTransport(
        handler
    )

    with ProviderHTTPClient(
        base_url="https://provider.test",
        max_retries=0,
        transport=transport,
    ) as client:
        with pytest.raises(
            ProviderDataError
        ):
            client.get_json(
                "/invalid"
            )