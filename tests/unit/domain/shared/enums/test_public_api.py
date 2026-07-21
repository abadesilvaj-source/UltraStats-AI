"""Testes da API pública dos enums esportivos."""

from ultrastats_ai.domain.shared import (
    CompetitionType,
    DomainEnum,
    MatchStatus,
    PhaseType,
    RoundType,
    SeasonStatus,
)
from ultrastats_ai.domain.shared.enums import (
    CompetitionType as EnumsCompetitionType,
    DomainEnum as EnumsDomainEnum,
    MatchStatus as EnumsMatchStatus,
    PhaseType as EnumsPhaseType,
    RoundType as EnumsRoundType,
    SeasonStatus as EnumsSeasonStatus,
)


def test_sport_enums_are_exported_by_public_apis() -> None:
    assert CompetitionType is EnumsCompetitionType
    assert DomainEnum is EnumsDomainEnum
    assert MatchStatus is EnumsMatchStatus
    assert PhaseType is EnumsPhaseType
    assert RoundType is EnumsRoundType
    assert SeasonStatus is EnumsSeasonStatus