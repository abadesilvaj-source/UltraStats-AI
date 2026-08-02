"""Providers complementares e orquestração tolerante a falhas."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum
from io import StringIO
from typing import Any, Mapping, Protocol
import os
import time

import httpx

from ultrastats_ai.infrastructure.providers.core import (
    ProviderConfigurationError,
    ProviderHealth,
    ProviderResponseError,
)


class DataCapability(StrEnum):
    FIXTURES = "fixtures"
    LIVE = "live"
    STATISTICS = "statistics"
    ODDS = "odds"
    HISTORICAL_ODDS = "historical_odds"
    EVENTS = "events"
    XG = "xg"
    LINEUPS = "lineups"
    COVERAGE = "coverage"
    INJURIES = "injuries"
    PLAYER_STATISTICS = "player_statistics"
    TEAM_STATISTICS = "team_statistics"
    PROVIDER_PREDICTIONS = "provider_predictions"
    LIVE_ODDS = "live_odds"


@dataclass(frozen=True, slots=True)
class SourceConfig:
    name: str
    base_url: str
    api_key: str | None = None
    timeout_seconds: float = 20

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.base_url.strip() or self.timeout_seconds <= 0:
            raise ProviderConfigurationError("Configuração da fonte é inválida.")


@dataclass(frozen=True, slots=True)
class SourceObservation:
    provider: str
    capability: DataCapability
    external_id: str
    values: Mapping[str, Any]
    observed_at: datetime


class DataSource(Protocol):
    name: str
    capabilities: frozenset[DataCapability]

    def collect(self, capability: DataCapability, **params: Any) -> tuple[SourceObservation, ...]: ...

    def health_check(self) -> ProviderHealth: ...

    def close(self) -> None: ...


class JsonDataSource:
    """Base HTTP pequena; adapters definem endpoints e normalização."""

    name = ""
    capabilities: frozenset[DataCapability] = frozenset()

    def __init__(
        self,
        config: SourceConfig,
        *,
        headers: Mapping[str, str] | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.config = config
        self.last_rate_limit: dict[str, int | str] = {}
        self.client = httpx.Client(
            base_url=config.base_url.rstrip("/"),
            headers=headers,
            timeout=config.timeout_seconds,
            transport=transport,
        )

    def _get(self, endpoint: str, params: Mapping[str, Any] | None = None) -> Any:
        retries = max(0, int(os.getenv("PROVIDER_RATE_LIMIT_RETRIES", "3")))
        response = None
        for attempt in range(retries + 1):
            try:
                response = self.client.get(endpoint, params=params)
            except httpx.RequestError as error:
                raise ProviderResponseError(f"{self.name}: falha de rede.") from error
            if response.status_code != 429 or attempt == retries:
                break
            retry_after = response.headers.get("retry-after")
            delay = float(retry_after) if retry_after and retry_after.replace(".", "", 1).isdigit() else min(30.0, 2 ** attempt)
            time.sleep(max(.1, delay))
        assert response is not None
        if response.status_code >= 400:
            raise ProviderResponseError(f"{self.name}: HTTP {response.status_code}.")
        self.last_rate_limit = {
            key.casefold(): (
                int(value) if str(value).isdigit() else str(value)
            )
            for key, value in response.headers.items()
            if key.casefold() in {
                "x-ratelimit-requests-limit",
                "x-ratelimit-requests-remaining",
                "x-ratelimit-limit",
                "x-ratelimit-remaining",
            }
        }
        try:
            return response.json()
        except ValueError as error:
            raise ProviderResponseError(f"{self.name}: JSON inválido.") from error

    def health_check(self) -> ProviderHealth:
        started = datetime.now(timezone.utc)
        try:
            self._health_request()
            available, message = True, "Provider disponível."
        except ProviderResponseError as error:
            available, message = False, str(error)
        elapsed = datetime.now(timezone.utc) - started
        return ProviderHealth(
            self.name,
            available,
            max(0, round(elapsed.total_seconds() * 1000)),
            message,
            datetime.now(timezone.utc),
        )

    def _health_request(self) -> None:
        raise NotImplementedError

    def close(self) -> None:
        self.client.close()


class ApiFootballSource(JsonDataSource):
    name = "api_football"
    capabilities = frozenset(
        {
            DataCapability.FIXTURES,
            DataCapability.LIVE,
            DataCapability.STATISTICS,
            DataCapability.ODDS,
            DataCapability.EVENTS,
            DataCapability.LINEUPS,
            DataCapability.COVERAGE,
            DataCapability.INJURIES,
            DataCapability.PLAYER_STATISTICS,
            DataCapability.TEAM_STATISTICS,
            DataCapability.PROVIDER_PREDICTIONS,
            DataCapability.LIVE_ODDS,
        }
    )

    def __init__(self, config: SourceConfig, *, transport: httpx.BaseTransport | None = None) -> None:
        if not config.api_key:
            raise ProviderConfigurationError("API_FOOTBALL_KEY é obrigatória.")
        super().__init__(
            config,
            headers={"x-apisports-key": config.api_key},
            transport=transport,
        )

    def _health_request(self) -> None:
        self._raise_api_errors(self._get("/status"))

    @staticmethod
    def _raise_api_errors(payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        errors = payload.get("errors")
        if not errors:
            return
        if isinstance(errors, dict):
            message = "; ".join(
                f"{key}: {value}" for key, value in errors.items()
            )
        elif isinstance(errors, list):
            message = "; ".join(str(value) for value in errors)
        else:
            message = str(errors)
        raise ProviderResponseError(
            f"api_football: resposta rejeitada ({message})."
        )

    def collect(self, capability: DataCapability, **params: Any) -> tuple[SourceObservation, ...]:
        endpoints = {
            DataCapability.FIXTURES: "/fixtures",
            DataCapability.LIVE: "/fixtures",
            DataCapability.STATISTICS: "/fixtures/statistics",
            DataCapability.ODDS: "/odds",
            DataCapability.EVENTS: "/fixtures/events",
            DataCapability.LINEUPS: "/fixtures/lineups",
            DataCapability.COVERAGE: "/leagues",
            DataCapability.INJURIES: "/injuries",
            DataCapability.PLAYER_STATISTICS: "/fixtures/players",
            DataCapability.TEAM_STATISTICS: "/teams/statistics",
            DataCapability.PROVIDER_PREDICTIONS: "/predictions",
            DataCapability.LIVE_ODDS: "/odds/live",
        }
        if capability not in self.capabilities:
            raise ValueError(f"Capacidade não suportada: {capability}.")
        query = dict(params)
        if capability is DataCapability.LIVE:
            query["live"] = query.get("live", "all")
        payload = self._get(endpoints[capability], query)
        self._raise_api_errors(payload)
        rows = payload.get("response", []) if isinstance(payload, dict) else []
        if isinstance(rows, dict):
            rows = [rows]
        # Odds e alguns catálogos são paginados. Ignorar ``paging.total``
        # fazia a aplicação armazenar somente a primeira página, parecendo
        # falta de cobertura do provedor. A paginação é limitada e preserva
        # os cabeçalhos de quota lidos por ``_get``.
        paging = payload.get("paging") if isinstance(payload, dict) else None
        current_page = int((paging or {}).get("current") or 1)
        total_pages = min(int((paging or {}).get("total") or 1), 100)
        if "page" not in query and total_pages > current_page:
            expanded = list(rows)
            for page in range(current_page + 1, total_pages + 1):
                page_payload = self._get(
                    endpoints[capability], {**query, "page": page}
                )
                self._raise_api_errors(page_payload)
                page_rows = (
                    page_payload.get("response", [])
                    if isinstance(page_payload, dict) else []
                )
                if isinstance(page_rows, dict):
                    page_rows = [page_rows]
                expanded.extend(page_rows)
            rows = expanded
        return tuple(
            _observation(self.name, capability, _external_id(row, index), row)
            for index, row in enumerate(rows)
            if isinstance(row, dict)
        )


class GoalApiSource(JsonDataSource):
    """Agenda complementar da GOAL API normalizada no contrato canônico."""

    name = "goal_api"
    capabilities = frozenset({DataCapability.FIXTURES, DataCapability.LIVE})

    def __init__(
        self,
        config: SourceConfig,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not config.api_key:
            raise ProviderConfigurationError("GOAL_API_KEY é obrigatória.")
        super().__init__(
            config,
            headers={"Authorization": f"Bearer {config.api_key}"},
            transport=transport,
        )

    def _health_request(self) -> None:
        self._get("/fixtures", {"limit": 1})

    def collect(
        self, capability: DataCapability, **params: Any
    ) -> tuple[SourceObservation, ...]:
        if capability not in self.capabilities:
            raise ValueError(f"Capacidade não suportada: {capability}.")
        query = dict(params)
        if capability is DataCapability.LIVE:
            query["live"] = query.get("live", "true")
        payload = self._get("/fixtures", query)
        rows = payload.get("data", []) if isinstance(payload, dict) else []
        return tuple(
            _observation(
                self.name,
                capability,
                str(row.get("id") or row.get("apiId") or index),
                _normalize_goal_fixture(row),
            )
            for index, row in enumerate(rows)
            if isinstance(row, dict)
        )


class ZafronixSource(JsonDataSource):
    """Agenda complementar da Copa do Mundo.

    O plano gratuito expõe partidas e placares ao vivo pelo contrato atualmente
    homologado. Estatísticas, eventos e escalações só devem ser anunciados
    quando houver endpoints específicos validados; tratar ``/matches`` como se
    entregasse qualquer capacidade produzia uma falsa cobertura.
    """

    name = "zafronix"
    capabilities = frozenset(
        {
            DataCapability.FIXTURES,
            DataCapability.LIVE,
        }
    )

    def __init__(
        self,
        config: SourceConfig,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not config.api_key:
            raise ProviderConfigurationError(
                "ZAFRONIX_API_KEY é obrigatória."
            )
        super().__init__(
            config,
            headers={"X-API-Key": config.api_key},
            transport=transport,
        )

    def _health_request(self) -> None:
        self._get("/health")

    def collect(
        self, capability: DataCapability, **params: Any
    ) -> tuple[SourceObservation, ...]:
        if capability not in self.capabilities:
            raise ValueError(f"Capacidade não suportada: {capability}.")
        query = dict(params)
        endpoint = "/matches/live" if capability is DataCapability.LIVE else "/matches"
        payload = self._get(endpoint, query)
        rows = payload.get("data", []) if isinstance(payload, dict) else []
        return tuple(
            _observation(
                self.name,
                capability,
                str(row.get("id") or index),
                _normalize_zafronix_fixture(row),
            )
            for index, row in enumerate(rows)
            if isinstance(row, dict)
        )


class OpenLigaDBSource(JsonDataSource):
    name = "openligadb"
    capabilities = frozenset({DataCapability.FIXTURES})

    def _health_request(self) -> None:
        self._get("/getavailableleagues")

    def collect(self, capability: DataCapability, **params: Any) -> tuple[SourceObservation, ...]:
        if capability is not DataCapability.FIXTURES:
            raise ValueError(f"Capacidade não suportada: {capability}.")
        league, season = str(params["league"]), str(params["season"])
        payload = self._get(f"/getmatchdata/{league}/{season}")
        rows = payload if isinstance(payload, list) else []
        return tuple(
            _observation(self.name, capability, _external_id(row, index), row)
            for index, row in enumerate(rows)
            if isinstance(row, dict)
        )


class StatsBombOpenDataSource(JsonDataSource):
    name = "statsbomb_open_data"
    capabilities = frozenset({DataCapability.EVENTS, DataCapability.XG})

    def _health_request(self) -> None:
        self._get("/competitions.json")

    def collect(self, capability: DataCapability, **params: Any) -> tuple[SourceObservation, ...]:
        if capability not in self.capabilities:
            raise ValueError(f"Capacidade não suportada: {capability}.")
        match_id = str(params["match_id"])
        payload = self._get(f"/events/{match_id}.json")
        rows = payload if isinstance(payload, list) else []
        observations = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            if capability is DataCapability.XG:
                shot = row.get("shot")
                if not isinstance(shot, dict) or "statsbomb_xg" not in shot:
                    continue
                values: Mapping[str, Any] = {
                    "match_id": match_id,
                    "team": row.get("team"),
                    "player": row.get("player"),
                    "minute": row.get("minute"),
                    "xg": shot["statsbomb_xg"],
                    "outcome": shot.get("outcome"),
                }
            else:
                values = row
            observations.append(
                _observation(self.name, capability, _external_id(row, index), values)
            )
        return tuple(observations)


class FootballDataUKSource(JsonDataSource):
    name = "football_data_uk"
    capabilities = frozenset({DataCapability.FIXTURES, DataCapability.HISTORICAL_ODDS})

    def _health_request(self) -> None:
        response = self.client.get("/")
        if response.status_code >= 400:
            raise ProviderResponseError(f"{self.name}: HTTP {response.status_code}.")

    def collect(self, capability: DataCapability, **params: Any) -> tuple[SourceObservation, ...]:
        if capability not in self.capabilities:
            raise ValueError(f"Capacidade não suportada: {capability}.")
        path = str(params["path"]).lstrip("/")
        try:
            response = self.client.get(f"/{path}")
        except httpx.RequestError as error:
            raise ProviderResponseError(f"{self.name}: falha de rede.") from error
        if response.status_code >= 400:
            raise ProviderResponseError(f"{self.name}: HTTP {response.status_code}.")
        rows = csv.DictReader(StringIO(response.text.lstrip("\ufeff")))
        result = []
        for index, row in enumerate(rows):
            values = {key: value for key, value in row.items() if key}
            external_id = "|".join(
                (values.get("Date", ""), values.get("HomeTeam", ""), values.get("AwayTeam", ""))
            ) or str(index)
            result.append(_observation(self.name, capability, external_id, values))
        return tuple(result)


class TheSportsDBSource(JsonDataSource):
    """Fonte gratuita de agenda, resultados, clubes e metadados."""

    name = "thesportsdb"
    capabilities = frozenset({DataCapability.FIXTURES})

    def _health_request(self) -> None:
        self._get("/all_sports.php")

    def collect(
        self, capability: DataCapability, **params: Any
    ) -> tuple[SourceObservation, ...]:
        if capability is not DataCapability.FIXTURES:
            raise ValueError(f"Capacidade não suportada: {capability}.")
        payload = self._get(
            "/eventsday.php",
            {"d": str(params["date"]), "s": "Soccer"},
        )
        rows = payload.get("events") or [] if isinstance(payload, dict) else []
        return tuple(
            _observation(
                self.name,
                capability,
                str(row.get("idEvent") or index),
                row,
            )
            for index, row in enumerate(rows)
            if isinstance(row, dict)
        )


class SportmonksSource(JsonDataSource):
    """Dados profundos das competições liberadas no plano Sportmonks."""

    name = "sportmonks"
    capabilities = frozenset(
        {
            DataCapability.FIXTURES,
            DataCapability.LIVE,
            DataCapability.EVENTS,
            DataCapability.LINEUPS,
            DataCapability.STATISTICS,
            DataCapability.XG,
        }
    )

    def __init__(
        self,
        config: SourceConfig,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not config.api_key:
            raise ProviderConfigurationError("SPORTMONKS_API_TOKEN é obrigatório.")
        super().__init__(config, transport=transport)

    def _parameters(self, params: Mapping[str, Any]) -> dict[str, Any]:
        result = dict(params)
        result["api_token"] = self.config.api_key
        return result

    def _health_request(self) -> None:
        self._get("/leagues", self._parameters({"per_page": 1}))

    def collect(
        self, capability: DataCapability, **params: Any
    ) -> tuple[SourceObservation, ...]:
        if capability not in self.capabilities:
            raise ValueError(f"Capacidade não suportada: {capability}.")
        includes = {
            DataCapability.FIXTURES: "participants;league;venue;state;scores",
            DataCapability.LIVE: (
                "participants;league;venue;state;scores;"
                "events;statistics.type"
            ),
            DataCapability.EVENTS: "events",
            DataCapability.LINEUPS: "lineups.player",
            DataCapability.STATISTICS: "statistics.type",
            DataCapability.XG: "xGFixture",
        }
        endpoint = (
            "/livescores/inplay"
            if capability is DataCapability.LIVE
            else f"/fixtures/date/{str(params['date'])}"
        )
        payload = self._get(
            endpoint,
            self._parameters({"include": includes[capability]}),
        )
        rows = payload.get("data") or [] if isinstance(payload, dict) else []
        return tuple(
            _observation(
                self.name,
                capability,
                str(row.get("id") or index),
                row,
            )
            for index, row in enumerate(rows)
            if isinstance(row, dict)
        )


class TheOddsApiSource(JsonDataSource):
    """Odds atuais de múltiplas casas, independentes do feed esportivo."""

    name = "the_odds_api"
    capabilities = frozenset({DataCapability.ODDS})

    def __init__(
        self,
        config: SourceConfig,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not config.api_key:
            raise ProviderConfigurationError("THE_ODDS_API_KEY é obrigatória.")
        super().__init__(config, transport=transport)

    def _parameters(self, params: Mapping[str, Any]) -> dict[str, Any]:
        result = dict(params)
        result["apiKey"] = self.config.api_key
        return result

    def _health_request(self) -> None:
        self._get("/sports", self._parameters({}))

    def collect(
        self, capability: DataCapability, **params: Any
    ) -> tuple[SourceObservation, ...]:
        if capability is not DataCapability.ODDS:
            raise ValueError(f"Capacidade não suportada: {capability}.")
        sport_keys = params.get("sport_keys") or ("upcoming",)
        observations: list[SourceObservation] = []
        for sport_key in sport_keys:
            try:
                payload = self._get(
                    f"/sports/{sport_key}/odds",
                    self._parameters(
                        {
                            "regions": params.get("regions", "eu"),
                            "markets": params.get("markets", "h2h,totals"),
                            "oddsFormat": "decimal",
                            "dateFormat": "iso",
                        }
                    ),
                )
            except ProviderResponseError as error:
                # As chaves de esportes disponíveis mudam ao longo da
                # temporada. Uma competição inativa não deve derrubar as
                # odds válidas coletadas das demais.
                if "HTTP 404" in str(error):
                    continue
                raise
            rows = payload if isinstance(payload, list) else []
            observations.extend(
                _observation(
                    self.name,
                    capability,
                    str(row.get("id") or index),
                    row,
                )
                for index, row in enumerate(rows)
                if isinstance(row, dict)
            )
        return tuple(observations)


@dataclass(frozen=True, slots=True)
class CollectionReport:
    capability: DataCapability
    observations: tuple[SourceObservation, ...]
    successful_sources: tuple[str, ...]
    failed_sources: Mapping[str, str]
    degraded: bool


class MultiSourceEngine:
    def __init__(self, sources: tuple[DataSource, ...], priority: Mapping[str, int]) -> None:
        self.sources = sources
        self.priority = priority

    def collect(self, capability: DataCapability, **params: Any) -> CollectionReport:
        source_params = params.pop("source_params", {})
        candidates = sorted(
            (source for source in self.sources if capability in source.capabilities),
            key=lambda source: (self.priority.get(source.name, 10_000), source.name),
        )
        observations: list[SourceObservation] = []
        successful: list[str] = []
        failed: dict[str, str] = {}
        for source in candidates:
            try:
                selected_params = dict(params)
                selected_params.update(source_params.get(source.name, {}))
                observations.extend(source.collect(capability, **selected_params))
                successful.append(source.name)
            except (ProviderResponseError, KeyError, ValueError) as error:
                failed[source.name] = str(error)
        return CollectionReport(
            capability,
            tuple(observations),
            tuple(successful),
            failed,
            bool(failed) or not successful,
        )

    def close(self) -> None:
        for source in self.sources:
            source.close()


def build_multi_source_engine(
    environment: Mapping[str, str] | None = None,
    *,
    transports: Mapping[str, httpx.BaseTransport] | None = None,
) -> MultiSourceEngine:
    """Monta fontes licenciáveis; API-Football fica desabilitada sem chave."""

    values = os.environ if environment is None else environment
    injected = transports or {}
    sources: list[DataSource] = []
    explicit_api_key = values.get("API_FOOTBALL_KEY")
    api_key = (
        explicit_api_key.strip()
        if explicit_api_key is not None
        else values.get("SPORTS_API_KEY", "").strip()
    )
    if api_key:
        sources.append(
            ApiFootballSource(
                SourceConfig(
                    "api_football",
                    values.get(
                        "API_FOOTBALL_BASE_URL",
                        values.get(
                            "SPORTS_API_BASE_URL",
                            "https://v3.football.api-sports.io",
                        ),
                    ),
                    api_key,
                ),
                transport=injected.get("api_football"),
            )
        )
    sportsdb_key = values.get("THESPORTSDB_API_KEY", "123").strip() or "123"
    sources.append(
        TheSportsDBSource(
            SourceConfig(
                "thesportsdb",
                values.get(
                    "THESPORTSDB_BASE_URL",
                    f"https://www.thesportsdb.com/api/v1/json/{sportsdb_key}",
                ),
                sportsdb_key,
            ),
            transport=injected.get("thesportsdb"),
        )
    )
    sportmonks_key = values.get("SPORTMONKS_API_TOKEN", "").strip()
    if sportmonks_key:
        sources.append(
            SportmonksSource(
                SourceConfig(
                    "sportmonks",
                    values.get(
                        "SPORTMONKS_BASE_URL",
                        "https://api.sportmonks.com/v3/football",
                    ),
                    sportmonks_key,
                ),
                transport=injected.get("sportmonks"),
            )
        )
    odds_key = values.get("THE_ODDS_API_KEY", "").strip()
    if odds_key:
        sources.append(
            TheOddsApiSource(
                SourceConfig(
                    "the_odds_api",
                    values.get(
                        "THE_ODDS_API_BASE_URL",
                        "https://api.the-odds-api.com/v4",
                    ),
                    odds_key,
                ),
                transport=injected.get("the_odds_api"),
            )
        )
    goal_key = values.get("GOAL_API_KEY", "").strip()
    if goal_key:
        sources.append(
            GoalApiSource(
                SourceConfig(
                    "goal_api",
                    values.get(
                        "GOAL_API_BASE_URL",
                        "https://api.goal-api.com/v1",
                    ),
                    goal_key,
                ),
                transport=injected.get("goal_api"),
            )
        )
    zafronix_key = values.get("ZAFRONIX_API_KEY", "").strip()
    if zafronix_key:
        sources.append(
            ZafronixSource(
                SourceConfig(
                    "zafronix",
                    values.get(
                        "ZAFRONIX_BASE_URL",
                        "https://api.zafronix.com/fifa/worldcup/v1",
                    ),
                    zafronix_key,
                ),
                transport=injected.get("zafronix"),
            )
        )
    sources.extend(
        (
            OpenLigaDBSource(
                SourceConfig(
                    "openligadb",
                    values.get("OPENLIGADB_BASE_URL", "https://api.openligadb.de"),
                ),
                transport=injected.get("openligadb"),
            ),
            FootballDataUKSource(
                SourceConfig(
                    "football_data_uk",
                    values.get(
                        "FOOTBALL_DATA_UK_BASE_URL",
                        "https://www.football-data.co.uk",
                    ),
                ),
                transport=injected.get("football_data_uk"),
            ),
            StatsBombOpenDataSource(
                SourceConfig(
                    "statsbomb_open_data",
                    values.get(
                        "STATSBOMB_OPEN_DATA_BASE_URL",
                        "https://raw.githubusercontent.com/statsbomb/open-data/master/data",
                    ),
                ),
                transport=injected.get("statsbomb_open_data"),
            ),
        )
    )
    # Reduz novas coletas sem apagar payloads históricos. A ausência da
    # variável preserva a composição legada para compatibilidade de bibliotecas
    # e testes; o ambiente operacional seleciona explicitamente sua fonte.
    active_provider_names = {
        name.strip()
        for name in values.get("ACTIVE_PROVIDERS", "").split(",")
        if name.strip()
    }
    if active_provider_names:
        excluded_sources = [
            source for source in sources
            if source.name not in active_provider_names
        ]
        sources = [
            source for source in sources
            if source.name in active_provider_names
        ]
        for source in excluded_sources:
            source.close()
        missing = active_provider_names.difference(
            source.name for source in sources
        )
        if missing:
            raise ValueError(
                "Provedor(es) ativo(s) sem configuração válida: "
                + ", ".join(sorted(missing))
            )
    configured = values.get(
        "PROVIDER_PRIORITY",
        "api_football,sportmonks,football_data,the_odds_api,thesportsdb,"
        "goal_api,zafronix,statsbomb_open_data,football_data_uk,openligadb",
    )
    priority = {
        name.strip(): index for index, name in enumerate(configured.split(",")) if name.strip()
    }
    return MultiSourceEngine(tuple(sources), priority)


@dataclass(frozen=True, slots=True)
class OddsSnapshot:
    provider: str
    match_id: str
    bookmaker: str
    market: str
    selection: str
    decimal_odds: Decimal
    captured_at: datetime

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (self.provider, self.match_id, self.bookmaker, self.market, self.selection)
        ) or self.decimal_odds <= 1:
            raise ValueError("Snapshot de odds inválido.")


def _external_id(row: Mapping[str, Any], fallback: int) -> str:
    for candidate in ("id", "fixture", "matchID", "match_id"):
        value = row.get(candidate)
        if isinstance(value, dict):
            value = value.get("id")
        if value is not None:
            return str(value)
    return str(fallback)


def _observation(
    provider: str,
    capability: DataCapability,
    external_id: str,
    values: Mapping[str, Any],
) -> SourceObservation:
    return SourceObservation(provider, capability, external_id, values, datetime.now(timezone.utc))


def _normalize_goal_fixture(row: Mapping[str, Any]) -> dict[str, Any]:
    status = str(row.get("matchStatus") or "").upper()
    status_map = {
        "NOT STARTED": "NS", "SCHEDULED": "NS", "TIMED": "NS",
        "LIVE": "LIVE", "IN PLAY": "LIVE", "IN_PLAY": "LIVE",
        "HALF TIME": "HT", "HALFTIME": "HT",
        "FINISHED": "FT", "FT": "FT", "POSTPONED": "PST",
        "CANCELLED": "CANC", "CANCELED": "CANC",
    }
    date = str(row.get("matchDate") or "")
    time = str(row.get("matchTime") or "00:00:00")
    kickoff = row.get("kickoffAt") or f"{date}T{time}"
    return {
        "fixture": {
            "id": row.get("id") or row.get("apiId"),
            "date": kickoff,
            "status": {"short": status_map.get(status, status or "NS")},
            "venue": {"name": row.get("matchStadium")},
        },
        "league": {
            "id": row.get("leagueId"),
            "name": row.get("leagueName"),
            "country": row.get("countryName"),
            "season": row.get("leagueYear"),
        },
        "teams": {
            "home": {
                "id": row.get("homeTeamId"),
                "name": row.get("homeTeamName"),
            },
            "away": {
                "id": row.get("awayTeamId"),
                "name": row.get("awayTeamName"),
            },
        },
        "goals": {
            "home": row.get("homeTeamScore"),
            "away": row.get("awayTeamScore"),
        },
        "_provider_payload": row,
    }


def _normalize_zafronix_fixture(row: Mapping[str, Any]) -> dict[str, Any]:
    raw_status = str(row.get("status") or "").casefold()
    if any(token in raw_status for token in ("final", "finished", "ft")):
        status = "FT"
    elif any(token in raw_status for token in ("live", "progress", "half")):
        status = "LIVE"
    elif "postpon" in raw_status:
        status = "PST"
    elif "cancel" in raw_status:
        status = "CANC"
    else:
        status = "NS"

    def team(value: Any, fallback: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return {
                "id": value.get("id") or value.get("code") or fallback,
                "name": value.get("name") or value.get("shortName") or fallback,
            }
        return {"id": fallback, "name": value or fallback}

    home = team(row.get("homeTeam"), row.get("homeRef") or "home")
    away = team(row.get("awayTeam"), row.get("awayRef") or "away")
    kickoff = (
        row.get("kickoffUtc")
        or row.get("kickoff")
        or row.get("date")
    )
    return {
        "fixture": {
            "id": row.get("id"),
            "date": kickoff,
            "status": {"short": status},
            "venue": {"name": row.get("stadium")},
        },
        "league": {
            "id": "WC",
            "name": "FIFA World Cup",
            "country": "International",
            "season": row.get("year"),
        },
        "teams": {"home": home, "away": away},
        "goals": {
            "home": row.get("homeScore"),
            "away": row.get("awayScore"),
        },
        "statistics": row.get("statistics"),
        "events": {
            "goals": row.get("goals"),
            "cards": row.get("cards"),
            "substitutions": row.get("substitutions"),
        },
        "lineups": row.get("lineups"),
        "weather": row.get("weather"),
        "_provider_payload": row,
    }
