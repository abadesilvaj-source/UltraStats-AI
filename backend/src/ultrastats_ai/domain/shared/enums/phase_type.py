"""Tipos canônicos de fase de competição."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class PhaseType(DomainEnum):
    """Representa uma fase dentro de uma competição."""

    QUALIFYING = "qualifying"
    LEAGUE_STAGE = "league_stage"
    GROUP_STAGE = "group_stage"
    ROUND_OF_32 = "round_of_32"
    ROUND_OF_16 = "round_of_16"
    QUARTER_FINAL = "quarter_final"
    SEMI_FINAL = "semi_final"
    THIRD_PLACE = "third_place"
    FINAL = "final"