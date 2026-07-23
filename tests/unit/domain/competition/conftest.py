import pytest

from ultrastats_ai.domain.competition import (
    Competition,
    Season,
    Stage,
)
from ultrastats_ai.domain.shared import (
    CompetitionCode,
    CompetitionId,
    CompetitionName,
    CompetitionType,
    Name,
    PhaseType,
    SeasonId,
    StageId,
)


@pytest.fixture
def competition():
    return Competition(
        id=CompetitionId.new(),
        code=CompetitionCode("BRA-A"),
        name=CompetitionName(
            "Campeonato Brasileiro Série A"
        ),
        competition_type=CompetitionType.LEAGUE,
    )


@pytest.fixture
def season(competition):
    return Season(
        id=SeasonId.new(),
        competition=competition,
        name=Name("2026"),
    )


@pytest.fixture
def stage(season):
    return Stage(
        id=StageId.new(),
        season=season,
        name=Name("Fase de grupos"),
        phase_type=PhaseType.GROUP_STAGE,
        sequence=1,
    )