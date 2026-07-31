"""Testes da API pública dos enums do domínio."""

from ultrastats_ai.domain.shared import (
    BetStatus,
    CompetitionType,
    DecisionType,
    DomainEnum,
    EventType,
    InterruptionType,
    MarketType,
    MatchStatus,
    MovementType,
    OfficialRole,
    ParticipantRole,
    PhaseType,
    PredictionStatus,
    RecommendationStatus,
    ReviewType,
    RiskClassification,
    RoundType,
    SeasonStatus,
)
from ultrastats_ai.domain.shared.enums import (
    BetStatus as EnumsBetStatus,
    CompetitionType as EnumsCompetitionType,
    DecisionType as EnumsDecisionType,
    DomainEnum as EnumsDomainEnum,
    EventType as EnumsEventType,
    InterruptionType as EnumsInterruptionType,
    MarketType as EnumsMarketType,
    MatchStatus as EnumsMatchStatus,
    MovementType as EnumsMovementType,
    OfficialRole as EnumsOfficialRole,
    ParticipantRole as EnumsParticipantRole,
    PhaseType as EnumsPhaseType,
    PredictionStatus as EnumsPredictionStatus,
    RecommendationStatus as EnumsRecommendationStatus,
    ReviewType as EnumsReviewType,
    RiskClassification as EnumsRiskClassification,
    RoundType as EnumsRoundType,
    SeasonStatus as EnumsSeasonStatus,
)


def test_domain_enums_are_exported_by_public_apis() -> None:
    assert BetStatus is EnumsBetStatus
    assert CompetitionType is EnumsCompetitionType
    assert DecisionType is EnumsDecisionType
    assert DomainEnum is EnumsDomainEnum
    assert EventType is EnumsEventType
    assert InterruptionType is EnumsInterruptionType
    assert MarketType is EnumsMarketType
    assert MatchStatus is EnumsMatchStatus
    assert MovementType is EnumsMovementType
    assert OfficialRole is EnumsOfficialRole
    assert ParticipantRole is EnumsParticipantRole
    assert PhaseType is EnumsPhaseType
    assert PredictionStatus is EnumsPredictionStatus
    assert RecommendationStatus is EnumsRecommendationStatus
    assert ReviewType is EnumsReviewType
    assert RiskClassification is EnumsRiskClassification
    assert RoundType is EnumsRoundType
    assert SeasonStatus is EnumsSeasonStatus