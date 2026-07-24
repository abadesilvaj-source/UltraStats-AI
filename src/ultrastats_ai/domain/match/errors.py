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


class InvalidMatchStatusTransitionError(MatchDomainError):
    """Indica uma transição operacional não permitida."""


class InvalidScheduleChangeError(MatchDomainError):
    """Indica uma alteração de agenda incompleta ou redundante."""


class DuplicateScheduleChangeError(MatchDomainError):
    """Indica identidade duplicada no histórico de agenda."""


class ScheduleChangeOwnershipError(MatchDomainError):
    """Indica histórico pertencente a outra partida."""


class InvalidMatchVenueError(MatchDomainError):
    """Indica um contexto de local inconsistente."""


class MatchVenueOwnershipError(MatchDomainError):
    """Indica local pertencente a outra partida."""


class DuplicateMatchVenueError(MatchDomainError):
    """Indica identidade duplicada no histórico de locais."""


class MultipleCurrentMatchVenuesError(MatchDomainError):
    """Indica mais de um local principal vigente."""
