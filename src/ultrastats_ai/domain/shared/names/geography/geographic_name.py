"""Tipo base para nomes de conceitos geográficos."""

from __future__ import annotations

from dataclasses import dataclass

from ultrastats_ai.domain.shared.names.base.proper_name import ProperName


@dataclass(frozen=True, slots=True)
class GeographicName(ProperName):
    """Nome canônico de um conceito relacionado à geografia."""