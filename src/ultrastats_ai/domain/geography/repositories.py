"""Contratos de persistência do domínio geográfico."""

from __future__ import annotations

from typing import Protocol

from ultrastats_ai.domain.geography.city import City
from ultrastats_ai.domain.geography.country import Country
from ultrastats_ai.domain.geography.history import (
    GeographyHistoryEntry,
)
from ultrastats_ai.domain.geography.region import Region
from ultrastats_ai.domain.geography.stadium import Stadium
from ultrastats_ai.domain.shared import CanonicalId


class CountryRepository(Protocol):
    """Contrato de persistência para países."""

    def get_by_id(
        self,
        country_id: CanonicalId,
    ) -> Country | None:
        """Retorna um país por sua identidade."""
        ...

    def save(self, country: Country) -> None:
        """Cria ou atualiza um país."""
        ...

    def delete(self, country_id: CanonicalId) -> None:
        """Remove um país por sua identidade."""
        ...

    def list_all(self) -> tuple[Country, ...]:
        """Retorna todos os países."""
        ...


class RegionRepository(Protocol):
    """Contrato de persistência para regiões."""

    def get_by_id(
        self,
        region_id: CanonicalId,
    ) -> Region | None:
        """Retorna uma região por sua identidade."""
        ...

    def list_by_country(
        self,
        country_id: CanonicalId,
    ) -> tuple[Region, ...]:
        """Retorna as regiões pertencentes a um país."""
        ...

    def save(self, region: Region) -> None:
        """Cria ou atualiza uma região."""
        ...

    def delete(self, region_id: CanonicalId) -> None:
        """Remove uma região por sua identidade."""
        ...


class CityRepository(Protocol):
    """Contrato de persistência para cidades."""

    def get_by_id(
        self,
        city_id: CanonicalId,
    ) -> City | None:
        """Retorna uma cidade por sua identidade."""
        ...

    def list_by_region(
        self,
        region_id: CanonicalId,
    ) -> tuple[City, ...]:
        """Retorna as cidades pertencentes a uma região."""
        ...

    def list_by_country(
        self,
        country_id: CanonicalId,
    ) -> tuple[City, ...]:
        """Retorna as cidades pertencentes a um país."""
        ...

    def save(self, city: City) -> None:
        """Cria ou atualiza uma cidade."""
        ...

    def delete(self, city_id: CanonicalId) -> None:
        """Remove uma cidade por sua identidade."""
        ...


class StadiumRepository(Protocol):
    """Contrato de persistência para estádios."""

    def get_by_id(
        self,
        stadium_id: CanonicalId,
    ) -> Stadium | None:
        """Retorna um estádio por sua identidade."""
        ...

    def list_by_city(
        self,
        city_id: CanonicalId,
    ) -> tuple[Stadium, ...]:
        """Retorna os estádios pertencentes a uma cidade."""
        ...

    def list_by_region(
        self,
        region_id: CanonicalId,
    ) -> tuple[Stadium, ...]:
        """Retorna os estádios pertencentes a uma região."""
        ...

    def list_by_country(
        self,
        country_id: CanonicalId,
    ) -> tuple[Stadium, ...]:
        """Retorna os estádios pertencentes a um país."""
        ...

    def save(self, stadium: Stadium) -> None:
        """Cria ou atualiza um estádio."""
        ...

    def delete(self, stadium_id: CanonicalId) -> None:
        """Remove um estádio por sua identidade."""
        ...


class GeographyHistoryRepository(Protocol):
    """Contrato de persistência do histórico geográfico."""

    def append(
        self,
        entry: GeographyHistoryEntry,
    ) -> None:
        """Persiste uma nova entrada de histórico."""
        ...

    def get_by_id(
        self,
        history_id: CanonicalId,
    ) -> GeographyHistoryEntry | None:
        """Retorna uma entrada de histórico por sua identidade."""
        ...

    def list_for_entity(
        self,
        entity_id: CanonicalId,
    ) -> tuple[GeographyHistoryEntry, ...]:
        """Retorna o histórico completo de uma entidade."""
        ...