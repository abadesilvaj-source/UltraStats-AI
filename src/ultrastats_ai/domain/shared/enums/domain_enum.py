"""Classe-base para enums canônicos do domínio."""

from __future__ import annotations

import re
from enum import Enum
from typing import Self

from ultrastats_ai.domain.shared.errors import DomainValidationError


class DomainEnum(str, Enum):
    """Base reutilizável para enums textuais do domínio."""

    def __str__(self) -> str:
        """Retorna o valor canônico do membro."""
        return self.value

    @classmethod
    def parse(cls, value: Self | str) -> Self:
        """Converte um membro ou string em um membro do enum."""
        if isinstance(value, cls):
            return value

        if not isinstance(value, str):
            raise TypeError(
                f"{cls.__name__}.parse deve receber string "
                f"ou {cls.__name__}."
            )

        normalized = cls._normalize_input(value)

        for member in cls:
            if member.value == normalized:
                return member

        raise DomainValidationError(
            f"{value!r} não é um valor válido para {cls.__name__}."
        )

    @classmethod
    def _normalize_input(cls, value: str) -> str:
        """Normaliza entradas textuais para snake_case minúsculo."""
        stripped = value.strip()

        if not stripped:
            raise DomainValidationError(
                f"{cls.__name__} não pode receber um valor vazio."
            )

        lowered = stripped.lower()
        normalized_separators = re.sub(r"[\s-]+", "_", lowered)

        return re.sub(r"_+", "_", normalized_separators)

    @classmethod
    def values(cls) -> tuple[str, ...]:
        """Retorna todos os valores canônicos do enum."""
        return tuple(member.value for member in cls)

    @classmethod
    def names(cls) -> tuple[str, ...]:
        """Retorna todos os nomes simbólicos do enum."""
        return tuple(member.name for member in cls)

    @classmethod
    def choices(cls) -> tuple[tuple[str, str], ...]:
        """Retorna pares de valor e nome para interfaces e formulários."""
        return tuple(
            (member.value, member.name)
            for member in cls
        )

    @classmethod
    def has_value(cls, value: object) -> bool:
        """Indica se o valor pode ser convertido para o enum."""
        try:
            cls.parse(value)  # type: ignore[arg-type]
        except (TypeError, DomainValidationError):
            return False

        return True