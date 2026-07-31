"""Tipos canônicos de competição esportiva."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class CompetitionType(DomainEnum):
    """Representa o formato estrutural de uma competição."""

    LEAGUE = "league"
    CUP = "cup"
    TOURNAMENT = "tournament"
    PLAYOFF = "playoff"
    FRIENDLY = "friendly"