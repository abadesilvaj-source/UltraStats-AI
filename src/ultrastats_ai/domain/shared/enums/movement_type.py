"""Tipos canônicos de movimentação de participantes."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class MovementType(DomainEnum):
    """Representa uma movimentação contratual ou esportiva."""

    TRANSFER = "transfer"
    LOAN = "loan"
    LOAN_RETURN = "loan_return"
    FREE_TRANSFER = "free_transfer"
    RELEASE = "release"
    CONTRACT_RENEWAL = "contract_renewal"
    PROMOTION = "promotion"
    DEMOTION = "demotion"
    RETIREMENT = "retirement"