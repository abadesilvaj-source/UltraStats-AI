"""Classe-base para Value Objects numéricos inteiros."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ultrastats_ai.domain.shared.errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class IntegerValue:
    """Representa um valor inteiro e imutável."""

    value: int | str

    def __post_init__(self) -> None:
        """Converte o valor recebido para inteiro e executa validações."""
        normalized = self._to_integer(self.value)

        object.__setattr__(self, "value", normalized)

        self._validate()

    @classmethod
    def _to_integer(cls, value: int | str) -> int:
        """Converte inteiro ou string inteira para int."""
        if isinstance(value, bool):
            raise TypeError(
                f"{cls.__name__} não aceita valores booleanos."
            )

        if isinstance(value, int):
            return value

        if isinstance(value, str):
            stripped = value.strip()

            if not stripped:
                raise DomainValidationError(
                    f"{cls.__name__} não pode ser vazio."
                )

            if not re.fullmatch(r"[+-]?\d+", stripped):
                raise DomainValidationError(
                    f"{cls.__name__} deve possuir um valor inteiro válido."
                )

            return int(stripped)

        raise TypeError(
            f"{cls.__name__} deve receber int ou str."
        )

    def _validate(self) -> None:
        """Permite que subclasses acrescentem regras específicas."""