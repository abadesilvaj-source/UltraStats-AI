"""Exceções compartilhadas pela camada de domínio."""


class DomainError(Exception):
    """Erro base para violações relacionadas ao domínio."""


class DomainValidationError(DomainError):
    """Erro lançado quando um valor de domínio é inválido."""


class InvariantViolationError(DomainError):
    """Erro lançado quando uma invariável do domínio é violada."""


class EntityNotFoundError(DomainError):
    """Erro lançado quando uma entidade obrigatória não é encontrada."""


class ResultAccessError(DomainError):
    """Erro lançado ao acessar incorretamente o conteúdo de um Result."""