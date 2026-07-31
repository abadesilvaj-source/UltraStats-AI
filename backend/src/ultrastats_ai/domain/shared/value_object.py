"""Abstração base para Value Objects."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValueObject:
    """Objeto de domínio definido exclusivamente por seus valores.

    Subclasses devem ser imutáveis e podem sobrescrever o método
    ``validate`` para proteger suas regras de criação.
    """

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Valida o estado do Value Object.

        A implementação padrão não possui regras adicionais.
        """