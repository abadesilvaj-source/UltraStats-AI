"""Persistência canônica isolada do domínio e do aplicativo legado."""

from ultrastats_ai.infrastructure.database.models import CanonicalBase
from ultrastats_ai.infrastructure.database.repositories import (
    SqlAlchemyAggregateRepository,
)
from ultrastats_ai.infrastructure.database.unit_of_work import (
    SqlAlchemyUnitOfWork,
)

__all__ = [
    "CanonicalBase",
    "SqlAlchemyAggregateRepository",
    "SqlAlchemyUnitOfWork",
]
