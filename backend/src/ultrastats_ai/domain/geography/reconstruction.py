"""Estados utilizados para reconstruir entidades geográficas."""

from __future__ import annotations

from dataclasses import dataclass, field

from ultrastats_ai.domain.geography.aliases import Aliases
from ultrastats_ai.domain.geography.city import City
from ultrastats_ai.domain.geography.country import Country
from ultrastats_ai.domain.geography.region import Region
from ultrastats_ai.domain.geography.stadium import Stadium
from ultrastats_ai.domain.shared import (
    CanonicalId,
    Coordinates,
    CountryCode,
    Name,
)


@dataclass(frozen=True, slots=True)
class CountryReconstruction:
    """Estado persistido necessário para reconstruir Country."""

    id: CanonicalId
    code: CountryCode
    name: Name
    aliases: Aliases = field(default_factory=Aliases.empty)
    coordinates: Coordinates | None = None

    def __post_init__(self) -> None:
        """Valida o estado sem criar uma nova identidade."""
        if not isinstance(self.id, CanonicalId):
            raise TypeError(
                "id deve ser uma instância de CanonicalId."
            )

        if not isinstance(self.code, CountryCode):
            raise TypeError(
                "code deve ser uma instância de CountryCode."
            )

        if not isinstance(self.name, Name):
            raise TypeError(
                "name deve ser uma instância de Name."
            )

        if not isinstance(self.aliases, Aliases):
            raise TypeError(
                "aliases deve ser uma instância de Aliases."
            )

        if (
            self.coordinates is not None
            and not isinstance(self.coordinates, Coordinates)
        ):
            raise TypeError(
                "coordinates deve ser uma instância de "
                "Coordinates ou None."
            )

    def restore(self) -> Country:
        """Reconstrói Country preservando sua identidade."""
        return Country(
            id=self.id,
            code=self.code,
            name=self.name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    @classmethod
    def from_entity(
        cls,
        country: Country,
    ) -> CountryReconstruction:
        """Captura o estado necessário para reconstruir Country."""
        if not isinstance(country, Country):
            raise TypeError(
                "country deve ser uma instância de Country."
            )

        return cls(
            id=country.id,
            code=country.code,
            name=country.name,
            aliases=country.aliases,
            coordinates=country.coordinates,
        )


@dataclass(frozen=True, slots=True)
class RegionReconstruction:
    """Estado persistido necessário para reconstruir Region."""

    id: CanonicalId
    country: Country
    name: Name
    aliases: Aliases = field(default_factory=Aliases.empty)
    coordinates: Coordinates | None = None

    def __post_init__(self) -> None:
        """Valida o estado sem criar uma nova identidade."""
        if not isinstance(self.id, CanonicalId):
            raise TypeError(
                "id deve ser uma instância de CanonicalId."
            )

        if not isinstance(self.country, Country):
            raise TypeError(
                "country deve ser uma instância de Country."
            )

        if not isinstance(self.name, Name):
            raise TypeError(
                "name deve ser uma instância de Name."
            )

        if not isinstance(self.aliases, Aliases):
            raise TypeError(
                "aliases deve ser uma instância de Aliases."
            )

        if (
            self.coordinates is not None
            and not isinstance(self.coordinates, Coordinates)
        ):
            raise TypeError(
                "coordinates deve ser uma instância de "
                "Coordinates ou None."
            )

    def restore(self) -> Region:
        """Reconstrói Region preservando sua identidade."""
        return Region(
            id=self.id,
            country=self.country,
            name=self.name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    @classmethod
    def from_entity(
        cls,
        region: Region,
    ) -> RegionReconstruction:
        """Captura o estado necessário para reconstruir Region."""
        if not isinstance(region, Region):
            raise TypeError(
                "region deve ser uma instância de Region."
            )

        return cls(
            id=region.id,
            country=region.country,
            name=region.name,
            aliases=region.aliases,
            coordinates=region.coordinates,
        )


@dataclass(frozen=True, slots=True)
class CityReconstruction:
    """Estado persistido necessário para reconstruir City."""

    id: CanonicalId
    region: Region
    name: Name
    aliases: Aliases = field(default_factory=Aliases.empty)
    coordinates: Coordinates | None = None

    def __post_init__(self) -> None:
        """Valida o estado sem criar uma nova identidade."""
        if not isinstance(self.id, CanonicalId):
            raise TypeError(
                "id deve ser uma instância de CanonicalId."
            )

        if not isinstance(self.region, Region):
            raise TypeError(
                "region deve ser uma instância de Region."
            )

        if not isinstance(self.name, Name):
            raise TypeError(
                "name deve ser uma instância de Name."
            )

        if not isinstance(self.aliases, Aliases):
            raise TypeError(
                "aliases deve ser uma instância de Aliases."
            )

        if (
            self.coordinates is not None
            and not isinstance(self.coordinates, Coordinates)
        ):
            raise TypeError(
                "coordinates deve ser uma instância de "
                "Coordinates ou None."
            )

    def restore(self) -> City:
        """Reconstrói City preservando sua identidade."""
        return City(
            id=self.id,
            region=self.region,
            name=self.name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    @classmethod
    def from_entity(
        cls,
        city: City,
    ) -> CityReconstruction:
        """Captura o estado necessário para reconstruir City."""
        if not isinstance(city, City):
            raise TypeError(
                "city deve ser uma instância de City."
            )

        return cls(
            id=city.id,
            region=city.region,
            name=city.name,
            aliases=city.aliases,
            coordinates=city.coordinates,
        )


@dataclass(frozen=True, slots=True)
class StadiumReconstruction:
    """Estado persistido necessário para reconstruir Stadium."""

    id: CanonicalId
    city: City
    name: Name
    aliases: Aliases = field(default_factory=Aliases.empty)
    coordinates: Coordinates | None = None

    def __post_init__(self) -> None:
        """Valida o estado sem criar uma nova identidade."""
        if not isinstance(self.id, CanonicalId):
            raise TypeError(
                "id deve ser uma instância de CanonicalId."
            )

        if not isinstance(self.city, City):
            raise TypeError(
                "city deve ser uma instância de City."
            )

        if not isinstance(self.name, Name):
            raise TypeError(
                "name deve ser uma instância de Name."
            )

        if not isinstance(self.aliases, Aliases):
            raise TypeError(
                "aliases deve ser uma instância de Aliases."
            )

        if (
            self.coordinates is not None
            and not isinstance(self.coordinates, Coordinates)
        ):
            raise TypeError(
                "coordinates deve ser uma instância de "
                "Coordinates ou None."
            )

    def restore(self) -> Stadium:
        """Reconstrói Stadium preservando sua identidade."""
        return Stadium(
            id=self.id,
            city=self.city,
            name=self.name,
            aliases=self.aliases,
            coordinates=self.coordinates,
        )

    @classmethod
    def from_entity(
        cls,
        stadium: Stadium,
    ) -> StadiumReconstruction:
        """Captura o estado necessário para reconstruir Stadium."""
        if not isinstance(stadium, Stadium):
            raise TypeError(
                "stadium deve ser uma instância de Stadium."
            )

        return cls(
            id=stadium.id,
            city=stadium.city,
            name=stadium.name,
            aliases=stadium.aliases,
            coordinates=stadium.coordinates,
        )