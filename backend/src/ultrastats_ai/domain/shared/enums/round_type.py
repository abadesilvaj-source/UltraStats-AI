"""Tipos canônicos de rodada esportiva."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class RoundType(DomainEnum):
    """Representa a natureza de uma rodada."""

    REGULAR = "regular"
    PRELIMINARY = "preliminary"
    QUALIFYING = "qualifying"
    GROUP = "group"
    KNOCKOUT = "knockout"
    PLAYOFF = "playoff"
    FINAL = "final"