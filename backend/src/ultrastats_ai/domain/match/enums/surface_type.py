"""Tipos de superfície esportiva."""

from ultrastats_ai.domain.shared.enums import DomainEnum


class SurfaceType(DomainEnum):
    """Classifica a superfície utilizada na partida."""

    NATURAL_GRASS = "natural_grass"
    HYBRID_GRASS = "hybrid_grass"
    ARTIFICIAL_TURF = "artificial_turf"
    SYNTHETIC_TURF = "synthetic_turf"
    DIRT = "dirt"
    SAND = "sand"
    INDOOR_SURFACE = "indoor_surface"
    OTHER = "other"
    UNKNOWN = "unknown"
