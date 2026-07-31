"""Tipos de perfil profissional do People Context."""

from ultrastats_ai.domain.shared import DomainEnum


class PeopleProfileType(DomainEnum):
    """Identifica o tipo de perfil profissional envolvido."""

    PLAYER = "player"
    COACH = "coach"
    REFEREE = "referee"
