"""Classe-base para Value Objects numéricos decimais."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import TypeAlias

from ultrastats_ai.domain.shared.errors import DomainValidationError


DecimalInput: TypeAlias = Decimal | int | float | str


@dataclass(frozen=True, slots=True)
class DecimalValue:
    """Representa um valor decimal finito e imutável."""

    value: DecimalInput

    def __post_init__(self) -> None:
        """Converte o valor recebido para Decimal e executa validações."""
        normalized = self._to_decimal(self.value)

        object.__setattr__(self, "value", normalized)

        self._validate()

    @classmethod
    def _to_decimal(cls, value: DecimalInput) -> Decimal:
        """Converte entradas numéricas para Decimal de maneira previsível."""
        if isinstance(value, bool):
            raise TypeError(
                f"{cls.__name__} não aceita valores booleanos."
            )

        if isinstance(value, str):
            stripped = value.strip()

            if not stripped:
                raise DomainValidationError(
                    f"{cls.__name__} não pode ser vazio."
                )

            raw_value: Decimal | int | str = stripped
        elif isinstance(value, Decimal):
            raw_value = value
        elif isinstance(value, int):
            raw_value = value
        elif isinstance(value, float):
            raw_value = str(value)
        else:
            raise TypeError(
                f"{cls.__name__} deve receber Decimal, int, float ou str."
            )

        try:
            decimal_value = Decimal(raw_value)
        except (InvalidOperation, ValueError):
            raise DomainValidationError(
                f"{cls.__name__} deve possuir um valor decimal válido."
            ) from None

        if not decimal_value.is_finite():
            raise DomainValidationError(
                f"{cls.__name__} deve possuir um valor decimal finito."
            )

        return decimal_value

    def _validate(self) -> None:
        """Permite que subclasses acrescentem regras específicas."""