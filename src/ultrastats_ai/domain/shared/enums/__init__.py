"""Enums canônicos compartilhados do domínio."""

from ultrastats_ai.domain.shared.enums.competition_type import (
    CompetitionType,
)
from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.match_status import MatchStatus
from ultrastats_ai.domain.shared.enums.phase_type import PhaseType
from ultrastats_ai.domain.shared.enums.round_type import RoundType
from ultrastats_ai.domain.shared.enums.season_status import SeasonStatus

__all__ = [
    "CompetitionType",
    "DomainEnum",
    "MatchStatus",
    "PhaseType",
    "RoundType",
    "SeasonStatus",
]