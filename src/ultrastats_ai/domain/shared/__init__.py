"""Abstrações fundamentais compartilhadas pelo domínio."""

from ultrastats_ai.domain.shared.aggregate_root import AggregateRoot
from ultrastats_ai.domain.shared.domain_event import DomainEvent
from ultrastats_ai.domain.shared.entity import Entity
from ultrastats_ai.domain.shared.errors import (
    DomainError,
    DomainValidationError,
    EntityNotFoundError,
    InvariantViolationError,
    ResultAccessError,
)
from ultrastats_ai.domain.shared.repository import Repository
from ultrastats_ai.domain.shared.result import Result
from ultrastats_ai.domain.shared.value_object import ValueObject

__all__ = [
    "AggregateRoot",
    "DomainError",
    "DomainEvent",
    "DomainValidationError",
    "Entity",
    "EntityNotFoundError",
    "InvariantViolationError",
    "Repository",
    "Result",
    "ResultAccessError",
    "ValueObject",
]