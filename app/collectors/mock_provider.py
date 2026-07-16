import json
from datetime import datetime
from pathlib import Path

from app.collectors.base import SportsDataCollector
from app.collectors.dtos import (
    CompetitionDTO,
    MatchDTO,
    TeamDTO,
)


class MockSportsCollector(
    SportsDataCollector
):
    """
    Collector de testes baseado em JSON local.

    Ele simula o comportamento de uma API real.
    """

    def __init__(
        self,
        file_path: str | Path,
    ) -> None:
        self.file_path = Path(
            file_path
        )

    @property
    def source_name(self) -> str:
        return "mock_provider"

    def _load_data(self) -> dict:
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: "
                f"{self.file_path}"
            )

        with self.file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "O arquivo do provedor deve "
                "conter um objeto JSON."
            )

        return data

    def fetch_competitions(
        self,
    ) -> list[CompetitionDTO]:
        data = self._load_data()

        rows = data.get(
            "competitions",
            [],
        )

        return [
            CompetitionDTO(
                source=self.source_name,
                external_id=str(
                    row["external_id"]
                ),
                name=row["name"],
                country=row.get(
                    "country"
                ),
                season=row.get(
                    "season"
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
        data = self._load_data()

        rows = data.get(
            "teams",
            [],
        )

        return [
            TeamDTO(
                source=self.source_name,
                external_id=str(
                    row["external_id"]
                ),
                name=row["name"],
                country=row.get(
                    "country"
                ),
                league=row.get(
                    "league"
                ),
            )
            for row in rows
        ]

    def fetch_matches(
        self,
    ) -> list[MatchDTO]:
        data = self._load_data()

        rows = data.get(
            "matches",
            [],
        )

        result = []

        for row in rows:
            kickoff_at = datetime.fromisoformat(
                row["kickoff_at"]
            )

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