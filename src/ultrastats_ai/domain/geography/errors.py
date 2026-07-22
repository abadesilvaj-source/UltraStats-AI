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


class CityNameAliasConflictError(GeographyDomainError):
    """Erro lançado quando o nome da cidade é repetido como alias."""


class StadiumNameAliasConflictError(GeographyDomainError):
    """Erro lançado quando o nome do estádio é repetido como alias."""


class GeographyHistoryError(GeographyDomainError):
    """Erro-base para violações do histórico geográfico."""


class DuplicateHistoryFieldError(GeographyHistoryError):
    """Erro lançado quando um campo aparece mais de uma vez no histórico."""


class EmptyHistoryChangesError(GeographyHistoryError):
    """Erro lançado quando uma atualização não possui alterações."""


class GeographyExternalIdentityError(GeographyDomainError):
    """Erro-base para identidades externas geográficas."""


class DuplicateExternalIdentityError(
    GeographyExternalIdentityError
):
    """Erro lançado quando uma identidade externa já está vinculada."""


class ExternalIdentityNotFoundError(
    GeographyExternalIdentityError
):
    """Erro lançado quando uma identidade externa não é encontrada."""