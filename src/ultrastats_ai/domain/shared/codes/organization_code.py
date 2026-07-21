"""Código canônico de organização."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.codes.code_value import CodeValue


@dataclass(frozen=True, slots=True)
class OrganizationCode(CodeValue):
    """Código canônico de organização."""