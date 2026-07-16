from datetime import datetime

from app.collectors.base import (
    SportsDataCollector,
)
from app.collectors.dtos import (
    CompetitionDTO,
    MatchDTO,
    TeamDTO,
)
from app.collectors.exceptions import (
    CollectorResponseError,
)
from app.collectors.http_client import (
    SportsHttpClient,
)


class NormalizedHttpSportsCollector(
    SportsDataCollector
):
    """
    Collector para uma API HTTP que já devolva
    o formato normalizado do UltraStats AI.

    Futuramente um collector específico poderá
    adaptar o formato real de cada provedor.
    """

    def __init__(
        self,
        client: SportsHttpClient,
        source_name: str,
        competitions_endpoint: str = (
            "/competitions"
        ),
        teams_endpoint: str = "/teams",
        matches_endpoint: str = "/matches",
    ) -> None:
        self.client = client
        self._source_name = source_name
        self.competitions_endpoint = (
            competitions_endpoint
        )
        self.teams_endpoint = teams_endpoint
        self.matches_endpoint = matches_endpoint

    @property
    def source_name(self) -> str:
        return self._source_name

    def _extract_rows(
        self,
        payload: dict | list,
        expected_key: str,
    ) -> list[dict]:
        if isinstance(payload, list):
            rows = payload

        else:
            rows = payload.get(
                expected_key
            )

            if rows is None:
                rows = payload.get(
                    "data"
                )

        if not isinstance(rows, list):
            raise CollectorResponseError(
                f"A resposta não possui uma lista "
                f"válida em '{expected_key}'."
            )

        if not all(
            isinstance(row, dict)
            for row in rows
        ):
            raise CollectorResponseError(
                "A lista retornada contém "
                "itens inválidos."
            )

        return rows

    def fetch_competitions(
        self,
    ) -> list[CompetitionDTO]:
        payload = self.client.get_json(
            self.competitions_endpoint
        )

        rows = self._extract_rows(
            payload,
            "competitions",
        )

        return [
            CompetitionDTO(
                source=self.source_name,
                external_id=str(
                    row["external_id"]
                ),
                name=str(row["name"]),
                country=row.get("country"),
                season=(
                    str(row["season"])
                    if row.get("season")
                    is not None
                    else None
                ),
                sport=row.get(
                    "sport",
                    "football",
                ),
            )
            for row in rows
        ]

    def fetch_teams(
        self,
    ) -> list[TeamDTO]:
        payload = self.client.get_json(
            self.teams_endpoint
        )

        rows = self._extract_rows(
            payload,
            "teams",
        )

        return [
            TeamDTO(
                source=self.source_name,
                external_id=str(
                    row["external_id"]
                ),
                name=str(row["name"]),
                country=row.get("country"),
                league=row.get("league"),
            )
            for row in rows
        ]

    def fetch_matches(
        self,
    ) -> list[MatchDTO]:
        payload = self.client.get_json(
            self.matches_endpoint
        )

        rows = self._extract_rows(
            payload,
            "matches",
        )

        result = []

        for row in rows:
            try:
                kickoff_at = (
                    datetime.fromisoformat(
                        str(
                            row["kickoff_at"]
                        ).replace(
                            "Z",
                            "+00:00",
                        )
                    )
                )

            except (
                KeyError,
                ValueError,
            ) as error:
                raise CollectorResponseError(
                    "Uma partida possui "
                    "kickoff_at inválido."
                ) from error

            result.append(
                MatchDTO(
                    source=self.source_name,
                    external_id=str(
                        row["external_id"]
                    ),
                    competition_external_id=str(
                        row[
                            "competition_external_id"
                        ]
                    ),
                    home_team_external_id=str(
                        row[
                            "home_team_external_id"
                        ]
                    ),
                    away_team_external_id=str(
                        row[
                            "away_team_external_id"
                        ]
                    ),
                    kickoff_at=kickoff_at,
                    status=row.get(
                        "status",
                        "scheduled",
                    ),
                    home_score=row.get(
                        "home_score"
                    ),
                    away_score=row.get(
                        "away_score"
                    ),
                    venue=row.get(
                        "venue"
                    ),
                )
            )

        return result