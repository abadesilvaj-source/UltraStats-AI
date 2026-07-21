"""Value Object para coordenadas geográficas."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ultrastats_ai.domain.shared.geographic.latitude import Latitude
from ultrastats_ai.domain.shared.geographic.longitude import Longitude


@dataclass(frozen=True, slots=True)
class Coordinates:
    """Representa um par ordenado de latitude e longitude."""

    latitude: Latitude
    longitude: Longitude

    def __post_init__(self) -> None:
        """Valida os tipos que compõem as coordenadas."""
        if not isinstance(self.latitude, Latitude):
            raise TypeError(
                "Coordinates.latitude deve ser um objeto Latitude."
            )

        if not isinstance(self.longitude, Longitude):
            raise TypeError(
                "Coordinates.longitude deve ser um objeto Longitude."
            )

    @property
    def decimal_pair(self) -> tuple[Decimal, Decimal]:
        """Retorna latitude e longitude como valores Decimal."""
        return (
            self.latitude.value,
            self.longitude.value,
        )

    @property
    def text_pair(self) -> str:
        """Retorna as coordenadas no formato latitude,longitude."""
        return f"{self.latitude.value},{self.longitude.value}"