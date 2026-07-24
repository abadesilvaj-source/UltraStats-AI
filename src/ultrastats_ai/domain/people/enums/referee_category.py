"""Categorias profissionais canônicas de árbitros."""

from ultrastats_ai.domain.shared import DomainEnum


class RefereeCategory(DomainEnum):
    """Representa o nível profissional conhecido de um árbitro."""

    LOCAL = "local"
    REGIONAL = "regional"
    NATIONAL = "national"
    CONTINENTAL = "continental"
    INTERNATIONAL = "international"
    ELITE = "elite"
    AMATEUR = "amateur"
    OTHER = "other"
    UNKNOWN = "unknown"