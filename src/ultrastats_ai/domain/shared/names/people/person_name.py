"""Value Object para nomes de pessoas."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.names.base.proper_name import ProperName


@dataclass(frozen=True, slots=True)
class PersonName(ProperName):
    """Nome canônico de uma pessoa."""