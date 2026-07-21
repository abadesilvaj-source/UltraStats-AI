"""Papéis canônicos de participantes em uma partida."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class ParticipantRole(DomainEnum):
    """Representa o papel de um participante em uma partida."""

    HOME = "home"
    AWAY = "away"
    NEUTRAL = "neutral"