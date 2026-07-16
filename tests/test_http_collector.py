import httpx
import pytest

from app.collectors import (
    NormalizedHttpSportsCollector,
    SportsHttpClient,
)
from app.collectors.exceptions import (
    CollectorAuthenticationError,
    CollectorResponseError,
)
from app.core.collector_settings import (
    CollectorSettings,
)


def create_settings() -> CollectorSettings:
    return CollectorSettings(
        base_url="https://sandbox.test",
        api_key="test-key",
        timeout=5.0,
        max_retries=0,
        retry_delay=0.0,
        sandbox=True,
    )


def test_http_collector_competitions() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        assert (
            request.headers[
                "Authorization"
            ]
            == "Bearer test-key"
        )

        return httpx.Response(
            200,
            json={
                "competitions": [
                    {
                        "external_id": "comp-1",
                        "name": "Liga de Teste",
                        "country": "Brasil",
                        "season": "2026",
                        "sport": "football",
                    }
                ]
            },
        )

    transport = httpx.MockTransport(
        handler
    )

    client = SportsHttpClient(
        settings=create_settings(),
        transport=transport,
    )

    try:
        collector = (
            NormalizedHttpSportsCollector(
                client=client,
                source_name="sandbox_test",
            )
        )

        competitions = (
            collector.fetch_competitions()
        )

        assert len(competitions) == 1
        assert (
            competitions[0].external_id
            == "comp-1"
        )
        assert (
            competitions[0].source
            == "sandbox_test"
        )

    finally:
        client.close()


def test_http_collector_teams() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "teams": [
                    {
                        "external_id": "team-1",
                        "name": "Equipe Teste",
                        "country": "Brasil",
                        "league": "Liga de Teste",
                    }
                ]
            },
        )

    client = SportsHttpClient(
        settings=create_settings(),
        transport=httpx.MockTransport(
            handler
        ),
    )

    try:
        collector = (
            NormalizedHttpSportsCollector(
                client=client,
                source_name="sandbox_test",
            )
        )

        teams = collector.fetch_teams()

        assert len(teams) == 1
        assert teams[0].name == "Equipe Teste"

    finally:
        client.close()


def test_authentication_error() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "message": "Unauthorized"
            },
        )

    client = SportsHttpClient(
        settings=create_settings(),
        transport=httpx.MockTransport(
            handler
        ),
    )

    try:
        with pytest.raises(
            CollectorAuthenticationError
        ):
            client.get_json(
                "/competitions"
            )

    finally:
        client.close()


def test_invalid_json_shape() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "competitions": "invalid"
            },
        )

    client = SportsHttpClient(
        settings=create_settings(),
        transport=httpx.MockTransport(
            handler
        ),
    )

    try:
        collector = (
            NormalizedHttpSportsCollector(
                client=client,
                source_name="sandbox_test",
            )
        )

        with pytest.raises(
            CollectorResponseError
        ):
            collector.fetch_competitions()

    finally:
        client.close()