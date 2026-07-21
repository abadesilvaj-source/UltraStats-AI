"""Enums canônicos compartilhados do domínio."""

from ultrastats_ai.domain.shared.enums.competition_type import (
    CompetitionType,
)
from ultrastats_ai.domain.shared.enums.decision_type import DecisionType
from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.event_type import EventType
from ultrastats_ai.domain.shared.enums.interruption_type import (
    InterruptionType,
)
from ultrastats_ai.domain.shared.enums.match_status import MatchStatus
from ultrastats_ai.domain.shared.enums.movement_type import MovementType
from ultrastats_ai.domain.shared.enums.official_role import OfficialRole
from ultrastats_ai.domain.shared.enums.participant_role import (
    ParticipantRole,
)
from ultrastats_ai.domain.shared.enums.phase_type import PhaseType
from ultrastats_ai.domain.shared.enums.review_type import ReviewType
from ultrastats_ai.domain.shared.enums.round_type import RoundType
from ultrastats_ai.domain.shared.enums.season_status import SeasonStatus

__all__ = [
    "CompetitionType",
    "DecisionType",
    "DomainEnum",
    "EventType",
    "InterruptionType",
    "MatchStatus",
    "MovementType",
    "OfficialRole",
    "ParticipantRole",
    "PhaseType",
    "ReviewType",
    "RoundType",
    "SeasonStatus",
]