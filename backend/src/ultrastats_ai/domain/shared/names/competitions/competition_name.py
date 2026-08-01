"""Value Object para nomes de competições esportivas."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.names.base.proper_name import ProperName


@dataclass(frozen=True, slots=True)
class CompetitionName(ProperName):
    """Nome canônico de uma competição esportiva."""