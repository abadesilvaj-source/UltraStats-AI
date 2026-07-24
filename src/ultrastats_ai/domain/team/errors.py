"""Erros específicos do Team Context."""

from ultrastats_ai.domain.shared import DomainValidationError


class TeamDomainError(DomainValidationError):
    """Erro-base das validações do Team Context."""


class DuplicateTeamAliasError(TeamDomainError):
    """Indica tentativa de adicionar um alias já existente."""


class TeamAliasNotFoundError(TeamDomainError):
    """Indica tentativa de remover um alias inexistente."""


class TeamNameAliasConflictError(TeamDomainError):
    """Indica conflito entre o nome principal e um alias."""


class TeamMembershipAlreadyExistsError(TeamDomainError):
    """Indica que o vínculo já pertence à equipe."""


class TeamMembershipNotFoundError(TeamDomainError):
    """Indica que o vínculo não pertence à equipe."""


class TeamMembershipOwnershipError(TeamDomainError):
    """Indica que o vínculo pertence a outra equipe."""


class SquadRegistrationAlreadyExistsError(TeamDomainError):
    """Indica que a inscrição já pertence à equipe."""


class SquadRegistrationNotFoundError(TeamDomainError):
    """Indica que a inscrição não pertence à equipe."""


class SquadRegistrationOwnershipError(TeamDomainError):
    """Indica que a inscrição pertence a outra equipe."""


class InvalidMembershipPeriodError(TeamDomainError):
    """Indica um período de vínculo inválido."""


class InvalidMembershipStateError(TeamDomainError):
    """Indica inconsistência entre período e status do vínculo."""


class InvalidRegistrationPeriodError(TeamDomainError):
    """Indica um período de inscrição inválido."""


class InvalidRegistrationStateError(TeamDomainError):
    """Indica inconsistência no estado da inscrição."""


class DuplicateSquadNumberError(TeamDomainError):
    """Indica número de camisa duplicado no mesmo elenco."""


class TeamAlreadyActiveError(TeamDomainError):
    """Indica tentativa de ativar uma equipe já ativa."""


class TeamAlreadyInactiveError(TeamDomainError):
    """Indica tentativa de inativar uma equipe já inativa."""


class InvalidTeamPeriodError(TeamDomainError):
    """Erro lançado quando o período de existência da equipe é inválido."""
