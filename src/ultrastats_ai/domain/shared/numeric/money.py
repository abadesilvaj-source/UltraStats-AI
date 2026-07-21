"""Value Object para valores monetários."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.numeric.decimal_value import (
    DecimalInput,
    DecimalValue,
)


@dataclass(frozen=True, slots=True)
class Money:
    """Representa um valor monetário e sua moeda."""

    amount: DecimalInput
    currency: str

    def __post_init__(self) -> None:
        normalized_amount = DecimalValue._to_decimal(self.amount)
        normalized_currency = self._normalize_currency(self.currency)

        object.__setattr__(self, "amount", normalized_amount)
        object.__setattr__(self, "currency", normalized_currency)

    @staticmethod
    def _normalize_currency(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError(
                "Money.currency deve ser uma string."
            )

        normalized = value.strip().upper()

        if not re.fullmatch(r"[A-Z]{3}", normalized):
            raise DomainValidationError(
                "Money.currency deve possuir exatamente três letras."
            )

        return normalized

    def add(self, other: Money) -> Money:
        """Soma valores pertencentes à mesma moeda."""
        self._ensure_same_currency(other)

        return Money(
            amount=self.amount + other.amount,
            currency=self.currency,
        )

    def subtract(self, other: Money) -> Money:
        """Subtrai valores pertencentes à mesma moeda."""
        self._ensure_same_currency(other)

        return Money(
            amount=self.amount - other.amount,
            currency=self.currency,
        )

    def _ensure_same_currency(self, other: Money) -> None:
        if not isinstance(other, Money):
            raise TypeError(
                "A operação monetária exige outro objeto Money."
            )

        if self.currency != other.currency:
            raise DomainValidationError(
                "Não é possível operar valores de moedas diferentes."
            )

    @property
    def is_negative(self) -> bool:
        """Indica se o valor monetário é negativo."""
        return self.amount < Decimal("0")