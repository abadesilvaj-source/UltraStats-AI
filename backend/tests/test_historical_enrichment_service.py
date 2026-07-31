from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Team
from app.services.historical_enrichment_service import (
    HistoricalEnrichmentService,
)
from ultrastats_ai.infrastructure.database.models import (
    CanonicalBase,
    FusionResultRecord,
)
from ultrastats_ai.infrastructure.providers import (
    DataCapability,
    SourceObservation,
)


def test_historical_results_update_team_ratings_once():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    CanonicalBase.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all((Team(name="Alpha FC"), Team(name="Beta FC")))
        session.flush()
        rows = tuple(
            SourceObservation(
                "football_data_uk",
                DataCapability.FIXTURES,
                f"row-{index}",
                {
                    "HomeTeam": "Alpha",
                    "AwayTeam": "Beta",
                    "FTHG": str(home),
                    "FTAG": str(away),
                },
                datetime.now(timezone.utc),
            )
            for index, (home, away) in enumerate(((3, 0), (2, 1), (4, 1)))
        )
        service = HistoricalEnrichmentService(session)
        first = service.process(rows)
        second = service.process(rows)
        session.commit()

        alpha = session.scalar(select(Team).where(Team.name == "Alpha FC"))
        assert first["teams_updated"] == 2
        assert second["skipped"] == 3
        assert alpha.attack_rating > 50
        marker = session.scalar(
            select(FusionResultRecord).where(
                FusionResultRecord.canonical_id.like(
                    "training:football_data_uk:%"
                )
            )
        )
        assert marker.values["sample_size"] == 3
