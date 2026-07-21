"""Testes da API pública dos enums do domínio."""

from ultrastats_ai.domain.shared import (
    CompetitionType,
    DecisionType,
    DomainEnum,
    EventType,
    InterruptionType,
    MatchStatus,
    MovementType,
    OfficialRole,
    ParticipantRole,
    PhaseType,
    ReviewType,
    RoundType,
    SeasonStatus,
)
from ultrastats_ai.domain.shared.enums import (
    CompetitionType as EnumsCompetitionType,
    DecisionType as EnumsDecisionType,
    DomainEnum as EnumsDomainEnum,
    EventType as EnumsEventType,
    InterruptionType as EnumsInterruptionType,
    MatchStatus as EnumsMatchStatus,
    MovementType as EnumsMovementType,
    OfficialRole as EnumsOfficialRole,
    ParticipantRole as EnumsParticipantRole,
    PhaseType as EnumsPhaseType,
    ReviewType as EnumsReviewType,
    RoundType as EnumsRoundType,
    SeasonStatus as EnumsSeasonStatus,
)


def test_domain_enums_are_exported_by_public_apis() -> None:
    assert CompetitionType is EnumsCompetitionType
    assert DecisionType is EnumsDecisionType
    assert DomainEnum is EnumsDomainEnum
    assert EventType is EnumsEventType
    assert InterruptionType is EnumsInterruptionType
    assert MatchStatus is EnumsMatchStatus
    assert MovementType is EnumsMovementType
    assert OfficialRole is EnumsOfficialRole
    assert ParticipantRole is EnumsParticipantRole
    assert PhaseType is EnumsPhaseType
    assert ReviewType is EnumsReviewType
    assert RoundType is EnumsRoundType
    assert SeasonStatus is EnumsSeasonStatus