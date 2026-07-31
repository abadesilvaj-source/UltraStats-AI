"""Código canônico de país."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.codes.code_value import CodeValue


@dataclass(frozen=True, slots=True)
class CountryCode(CodeValue):
    """Código canônico de país."""

    def __post_init__(self) -> None:
        super().__post_init__()

        if len(self.value) != 3:
            raise ValueError(
                "CountryCode deve possuir exatamente 3 caracteres."
            )

        if not self.value.isalpha():
            raise ValueError(
                "CountryCode aceita apenas letras de A a Z."
            )