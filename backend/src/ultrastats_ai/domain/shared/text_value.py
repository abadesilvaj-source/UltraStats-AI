"""Infraestrutura compartilhada para Value Objects textuais."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import ClassVar, Pattern

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class TextValue(ValueObject):
    """Value Object base para valores textuais canônicos.

    A classe centraliza:

    - validação de tipo;
    - normalização Unicode;
    - remoção de espaços nas extremidades;
    - redução de espaços internos consecutivos;
    - validação de comprimento;
    - validação opcional por expressão regular;
    - imutabilidade;
    - representação textual.
    """

    value: str

    MIN_LENGTH: ClassVar[int] = 1
    MAX_LENGTH: ClassVar[int] = 255

    ALLOW_EMPTY: ClassVar[bool] = False
    COLLAPSE_WHITESPACE: ClassVar[bool] = True

    UNICODE_NORMALIZATION_FORM: ClassVar[str] = "NFKC"

    PATTERN: ClassVar[Pattern[str] | None] = None

    def __post_init__(self) -> None:
        """Normaliza e valida o valor textual."""

        if not isinstance(self.value, str):
            raise DomainValidationError(
                f"{type(self).__name__} deve receber uma string."
            )

        normalized_value = self.normalize(self.value)

        object.__setattr__(self, "value", normalized_value)

        self.validate()

    @classmethod
    def normalize(cls, value: str) -> str:
        """Normaliza um valor textual.

        A normalização padrão aplica:

        1. normalização Unicode NFKC;
        2. remoção de espaços nas extremidades;
        3. redução de sequências de espaços internos.
        """

        normalized_value = unicodedata.normalize(
            cls.UNICODE_NORMALIZATION_FORM,
            value,
        )

        if cls.COLLAPSE_WHITESPACE:
            normalized_value = " ".join(normalized_value.split())
        else:
            normalized_value = normalized_value.strip()

        return normalized_value

    def validate(self) -> None:
        """Valida o conteúdo textual normalizado."""

        value_length = len(self.value)

        if not self.ALLOW_EMPTY and value_length == 0:
            raise DomainValidationError(
                f"{type(self).__name__} não pode ser vazio."
            )

        if value_length < self.MIN_LENGTH:
            raise DomainValidationError(
                f"{type(self).__name__} deve possuir pelo menos "
                f"{self.MIN_LENGTH} caractere(s)."
            )

        if value_length > self.MAX_LENGTH:
            raise DomainValidationError(
                f"{type(self).__name__} deve possuir no máximo "
                f"{self.MAX_LENGTH} caractere(s)."
            )

        if self.PATTERN is not None and self.PATTERN.fullmatch(self.value) is None:
            raise DomainValidationError(
                f"{type(self).__name__} possui formato inválido: "
                f"{self.value!r}."
            )

        self.validate_specific_rules()

    def validate_specific_rules(self) -> None:
        """Executa validações adicionais definidas por subclasses.

        Subclasses podem sobrescrever este método sem precisar repetir as
        validações básicas de texto.
        """

    def __str__(self) -> str:
        """Retorna o valor textual normalizado."""

        return self.value


def compile_text_pattern(pattern: str) -> Pattern[str]:
    """Compila uma expressão regular destinada a tipos textuais.

    Args:
        pattern: Expressão regular textual.

    Returns:
        Expressão regular compilada.
    """

    return re.compile(pattern)