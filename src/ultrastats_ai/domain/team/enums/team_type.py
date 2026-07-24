"""Tipos de equipe reconhecidos pelo Team Context."""

from ultrastats_ai.domain.shared import DomainEnum


class TeamType(DomainEnum):
    """Classifica a natureza institucional da equipe."""

    CLUB = "club"
    NATIONAL_TEAM = "national_team"
    RESERVE_TEAM = "reserve_team"
    YOUTH_TEAM = "youth_team"
    WOMEN_TEAM = "women_team"
    AMATEUR_TEAM = "amateur_team"
    UNKNOWN = "unknown"