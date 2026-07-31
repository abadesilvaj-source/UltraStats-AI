"""Condições contextuais da superfície esportiva."""

from ultrastats_ai.domain.shared.enums import DomainEnum


class SurfaceCondition(DomainEnum):
    """Classifica a condição observada da superfície."""

    EXCELLENT = "excellent"
    GOOD = "good"
    REGULAR = "regular"
    POOR = "poor"
    DAMAGED = "damaged"
    DRY = "dry"
    WET = "wet"
    WATERLOGGED = "waterlogged"
    FROZEN = "frozen"
    SNOW_COVERED = "snow_covered"
    MUDDY = "muddy"
    UNEVEN = "uneven"
    OTHER = "other"
    UNKNOWN = "unknown"
