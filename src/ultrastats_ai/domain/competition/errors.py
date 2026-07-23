"""Erros específicos do contexto de competições."""

from ultrastats_ai.domain.shared import InvariantViolationError


class CompetitionDomainError(InvariantViolationError):
    """Erro-base do contexto competitivo."""


class DuplicateAliasError(CompetitionDomainError):
    """Alias duplicado."""


class AliasNotFoundError(CompetitionDomainError):
    """Alias inexistente."""


class NameAliasConflictError(CompetitionDomainError):
    """Nome principal repetido como alias."""


class InvalidSeasonTransitionError(CompetitionDomainError):
    """Transição inválida de estado da temporada."""


class CompetitionHierarchyError(CompetitionDomainError):
    """Relacionamento incompatível na hierarquia competitiva."""


class DuplicateTieMatchError(CompetitionDomainError):
    """Partida duplicada em um confronto."""


class DuplicateTieMatchSequenceError(CompetitionDomainError):
    """Sequência duplicada em um confronto."""


class DuplicateHistoryFieldError(CompetitionDomainError):
    """Campo duplicado em uma entrada de histórico."""


class EmptyHistoryChangesError(CompetitionDomainError):
    """Atualização histórica sem alterações."""