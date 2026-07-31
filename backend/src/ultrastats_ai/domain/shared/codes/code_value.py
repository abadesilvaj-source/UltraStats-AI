"""Tipo base para códigos canônicos do domínio."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar

from ultrastats_ai.domain.shared.text_value import TextValue


@dataclass(frozen=True, slots=True)
class CodeValue(TextValue):
    """Código canônico interno do domínio."""

    MAX_LENGTH: ClassVar[int] = 64

    _ALLOWED_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^[A-Z0-9][A-Z0-9._-]*$"
    )

    def __post_init__(self) -> None:
        """Normaliza e valida o código canônico."""

        if not isinstance(self.value, str):
            raise TypeError("CodeValue deve receber um valor do tipo str.")

        normalized_value = self.value.strip().upper()

        object.__setattr__(self, "value", normalized_value)

        if not normalized_value:
            raise ValueError("CodeValue não pode ser vazio.")

        if len(normalized_value) > self.MAX_LENGTH:
            raise ValueError(
                f"CodeValue não pode exceder {self.MAX_LENGTH} caracteres."
            )

        if not self._ALLOWED_PATTERN.fullmatch(normalized_value):
            raise ValueError(
                "CodeValue aceita apenas letras de A a Z, números, "
                "ponto, hífen e underscore."
            )