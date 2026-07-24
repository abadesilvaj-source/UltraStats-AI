"""Erros específicos do Match Context."""

from ultrastats_ai.domain.shared.errors import DomainError


class MatchDomainError(DomainError):
    """Erro-base do Match Context."""


class InvalidMatchScheduleError(MatchDomainError):
    """Indica programação incompatível com o estado da partida."""


class InvalidMatchParticipantsError(MatchDomainError):
    """Indica composição inválida dos participantes da partida."""


class MatchParticipantOwnershipError(MatchDomainError):
    """Indica participante pertencente a outra partida."""


class MatchParticipantNotFoundError(MatchDomainError):
    """Indica que um participante não pertence à partida."""


class DuplicateMatchParticipantError(MatchDomainError):
    """Indica identidade, equipe, papel ou ordem duplicada."""
