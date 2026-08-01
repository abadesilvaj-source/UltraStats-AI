from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from app.providers.http_client import (
    ProviderHTTPClient,
)


class ProviderCapability(StrEnum):
    """
    Recursos que um provider pode oferecer.
    """

    COMPETITIONS = "competitions"
    TEAMS = "teams"
    MATCHES = "matches"
    STANDINGS = "standings"
    PLAYERS = "players"
    LINEUPS = "lineups"
    INJURIES = "injuries"
    MATCH_EVENTS = "match_events"
    MATCH_STATISTICS = "match_statistics"
    ODDS = "odds"
    EXPECTED_GOALS = "expected_goals"


@dataclass(
    frozen=True,
    slots=True,
)
class ProviderInfo:
    """
    Informações públicas sobre um provider.
    """

    name: str
    display_name: str
    capabilities: frozenset[
        ProviderCapability
    ]
    requires_api_key: bool = True
    official_api: bool = True


@dataclass(
    frozen=True,
    slots=True,
)
class ProviderHealthResult:
    """
    Resultado de uma verificação de saúde.
    """

    provider_name: str
    available: bool
    message: str
    details: dict[str, Any] | None = None


class BaseProvider(ABC):
    """
    Contrato obrigatório para todos os
    providers esportivos do UltraStats AI.
    """

    info: ProviderInfo

    def __init__(
        self,
        *,
        http_client: (
            ProviderHTTPClient | None
        ) = None,
    ) -> None:
        self._http_client = http_client

    @property
    def name(
        self,
    ) -> str:
        return self.info.name

    @property
    def display_name(
        self,
    ) -> str:
        return self.info.display_name

    @property
    def capabilities(
        self,
    ) -> frozenset[
        ProviderCapability
    ]:
        return self.info.capabilities

    @property
    def http_client(
        self,
    ) -> ProviderHTTPClient:
        if self._http_client is None:
            raise RuntimeError(
                f"O provider '{self.name}' não "
                "possui cliente HTTP configurado."
            )

        return self._http_client

    def supports(
        self,
        capability: ProviderCapability,
    ) -> bool:
        """
        Informa se o provider suporta uma
        determinada capacidade.
        """

        return capability in self.capabilities

    @abstractmethod
    def health_check(
        self,
    ) -> ProviderHealthResult:
        """
        Verifica se o provider está
        disponível e configurado.
        """

    def close(
        self,
    ) -> None:
        """
        Libera os recursos utilizados
        pelo provider.
        """

        if self._http_client is not None:
            self._http_client.close()

    def __enter__(
        self,
    ) -> BaseProvider:
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        self.close()