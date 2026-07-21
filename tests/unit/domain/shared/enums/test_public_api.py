"""Testes da API pública dos enums do domínio."""

from ultrastats_ai.domain.shared import (
    CompetitionType,
    DomainEnum,
    MatchStatus,
    MovementType,
    OfficialRole,
    ParticipantRole,
    PhaseType,
    RoundType,
    SeasonStatus,
)
from ultrastats_ai.domain.shared.enums import (
    CompetitionType as EnumsCompetitionType,
    DomainEnum as EnumsDomainEnum,
    MatchStatus as EnumsMatchStatus,
    MovementType as EnumsMovementType,
    OfficialRole as EnumsOfficialRole,
    ParticipantRole as EnumsParticipantRole,
    PhaseType as EnumsPhaseType,
    RoundType as EnumsRoundType,
    SeasonStatus as EnumsSeasonStatus,
)


def test_domain_enums_are_exported_by_public_apis() -> None:
    assert CompetitionType is EnumsCompetitionType
    assert DomainEnum is EnumsDomainEnum
    assert MatchStatus is EnumsMatchStatus
    assert MovementType is EnumsMovementType
    assert OfficialRole is EnumsOfficialRole
    assert ParticipantRole is EnumsParticipantRole
    assert PhaseType is EnumsPhaseType
    assert RoundType is EnumsRoundType
    assert SeasonStatus is EnumsSeasonStatus