"""Código canônico de competição."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.codes.code_value import CodeValue


@dataclass(frozen=True, slots=True)
class CompetitionCode(CodeValue):
    """Código canônico de competição."""