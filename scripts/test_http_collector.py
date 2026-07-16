import httpx

from app.collectors import (
    NormalizedHttpSportsCollector,
    SportsHttpClient,
)
from app.core.collector_settings import (
    CollectorSettings,
)
from app.core.logging_config import (
    configure_collector_logging,
)


def mock_handler(
    request: httpx.Request,
) -> httpx.Response:
    if request.url.path == "/competitions":
        return httpx.Response(
            200,
            json={
                "competitions": [
                    {
                        "external_id": (
                            "sandbox-comp-1"
                        ),
                        "name": (
                            "Competição Sandbox"
                        ),
                        "country": "Brasil",
                        "season": "2026",
                        "sport": "football",
                    }
                ]
            },
        )

    if request.url.path == "/teams":
        return httpx.Response(
            200,
            json={
                "teams": []
            },
        )

    if request.url.path == "/matches":
        return httpx.Response(
            200,
            json={
                "matches": []
            },
        )

    return httpx.Response(
        404,
        json={
            "message": "Not found"
        },
    )


def main() -> None:
    configure_collector_logging()

    settings = CollectorSettings(
        base_url="https://sandbox.test",
        api_key="test-key",
        timeout=5.0,
        max_retries=1,
        retry_delay=0.0,
        sandbox=True,
    )

    transport = httpx.MockTransport(
        mock_handler
    )

    with SportsHttpClient(
        settings=settings,
        transport=transport,
    ) as client:
        collector = (
            NormalizedHttpSportsCollector(
                client=client,
                source_name=(
                    "sandbox_provider"
                ),
            )
        )

        print(
            collector.fetch_competitions()
        )

        print(
            collector.fetch_teams()
        )

        print(
            collector.fetch_matches()
        )


if __name__ == "__main__":
    main()