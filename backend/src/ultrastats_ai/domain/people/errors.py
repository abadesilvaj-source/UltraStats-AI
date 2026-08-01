"""Erros específicos do People Context."""

from ultrastats_ai.domain.shared import DomainValidationError


class PeopleDomainError(DomainValidationError):
    """Erro-base das validações do People Context."""


class DuplicatePersonAliasError(PeopleDomainError):
    """Indica que um alias já pertence à pessoa."""


class PersonAliasNotFoundError(PeopleDomainError):
    """Indica que o alias informado não pertence à pessoa."""


class PersonNameAliasConflictError(PeopleDomainError):
    """Indica conflito entre o nome principal e um alias."""


class PersonProfileAlreadyExistsError(PeopleDomainError):
    """Indica que a pessoa já possui o perfil solicitado."""


class PersonProfileNotFoundError(PeopleDomainError):
    """Indica que a pessoa não possui o perfil solicitado."""


class PersonProfileOwnershipError(PeopleDomainError):
    """Indica que o perfil pertence a outra pessoa."""


class InvalidProfessionalPeriodError(PeopleDomainError):
    """Indica um período profissional inválido."""


class InvalidRetirementStateError(PeopleDomainError):
    """Indica inconsistência entre aposentadoria e status."""


class PersonAlreadyInactiveError(PeopleDomainError):
    """Indica tentativa de inativar pessoa já inativa."""


class PersonAlreadyActiveError(PeopleDomainError):
    """Indica tentativa de ativar pessoa já ativa."""