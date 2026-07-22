"""Exceções específicas do domínio geográfico."""

from ultrastats_ai.domain.shared.errors import DomainValidationError


class GeographyDomainError(DomainValidationError):
    """Erro-base para violações das regras do domínio geográfico."""


class DuplicateAliasError(GeographyDomainError):
    """Erro lançado quando um alias já existe na coleção."""


class AliasNotFoundError(GeographyDomainError):
    """Erro lançado quando um alias solicitado não existe."""


class CountryNameAliasConflictError(GeographyDomainError):
    """Erro lançado quando o nome principal é repetido como alias."""


class RegionNameAliasConflictError(GeographyDomainError):
    """Erro lançado quando o nome da região é repetido como alias."""