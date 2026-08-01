from abc import ABC, abstractmethod

from app.collectors.dtos import (
    CompetitionDTO,
    MatchDTO,
    TeamDTO,
)


class SportsDataCollector(ABC):
    """
    Contrato obrigatório para qualquer
    provedor de dados esportivos.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Nome interno do provedor."""

        raise NotImplementedError

    @abstractmethod
    def fetch_competitions(
        self,
    ) -> list[CompetitionDTO]:
        """Busca competições no provedor."""

        raise NotImplementedError

    @abstractmethod
    def fetch_teams(
        self,
    ) -> list[TeamDTO]:
        """Busca equipes no provedor."""

        raise NotImplementedError

    @abstractmethod
    def fetch_matches(
        self,
    ) -> list[MatchDTO]:
        """Busca partidas no provedor."""

        raise NotImplementedError