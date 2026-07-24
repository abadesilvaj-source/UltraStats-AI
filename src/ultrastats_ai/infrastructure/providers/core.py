"""Contratos e primitivas da integração canônica com providers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import os
import time
from typing import Any, Protocol

import httpx


class ProviderError(RuntimeError):
    pass


class ProviderConfigurationError(ProviderError):
    pass


class ProviderResponseError(ProviderError):
    pass


class ProviderCapability(StrEnum):
    COMPETITIONS = "competitions"
    TEAMS = "teams"
    MATCHES = "matches"
    STANDINGS = "standings"


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    api_token: str
    base_url: str = "https://api.football-data.org/v4"
    requests_per_minute: int = 10
    timeout_seconds: float = 15
    max_retries: int = 3

    def __post_init__(self) -> None:
        if not self.api_token.strip():
            raise ProviderConfigurationError("Token do provider é obrigatório.")
        if self.requests_per_minute <= 0 or self.timeout_seconds <= 0 or self.max_retries < 0:
            raise ProviderConfigurationError("Limites HTTP inválidos.")

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> ProviderConfig:
        values = os.environ if environment is None else environment
        token = values.get("FOOTBALL_DATA_API_TOKEN", "")
        return cls(
            api_token=token,
            base_url=values.get(
                "FOOTBALL_DATA_BASE_URL",
                "https://api.football-data.org/v4",
            ),
            requests_per_minute=int(values.get("PROVIDER_DEFAULT_REQUESTS_PER_MINUTE", "10")),
            timeout_seconds=float(values.get("PROVIDER_HTTP_TIMEOUT_SECONDS", "15")),
            max_retries=int(values.get("PROVIDER_HTTP_MAX_RETRIES", "3")),
        )


@dataclass(frozen=True, slots=True)
class RawProviderPayload:
    provider: str
    resource: str
    external_id: str | None
    payload: Mapping[str, Any]
    collected_at: datetime


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    provider: str
    available: bool
    latency_ms: int
    message: str
    checked_at: datetime


class RawPayloadStore(Protocol):
    def save(self, payload: RawProviderPayload) -> bool: ...


class InMemoryRawPayloadStore:
    def __init__(self) -> None:
        self.payloads: list[RawProviderPayload] = []
        self._keys: set[tuple[str, str, str | None, str]] = set()

    def save(self, payload: RawProviderPayload) -> bool:
        key = (
            payload.provider,
            payload.resource,
            payload.external_id,
            repr(sorted(payload.payload.items())),
        )
        if key in self._keys:
            return False
        self._keys.add(key)
        self.payloads.append(payload)
        return True


class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.interval = 60 / requests_per_minute
        self.clock, self.sleeper, self._last = clock, sleeper, None

    def acquire(self) -> None:
        now = self.clock()
        if self._last is not None:
            remaining = self.interval - (now - self._last)
            if remaining > 0:
                self.sleeper(remaining)
                now = self.clock()
        self._last = now


class ProviderHTTPClient:
    def __init__(
        self,
        config: ProviderConfig,
        *,
        transport: httpx.BaseTransport | None = None,
        limiter: RateLimiter | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config, self.limiter, self.sleeper = config, limiter, sleeper
        self.client = httpx.Client(
            base_url=config.base_url.rstrip("/"),
            headers={"X-Auth-Token": config.api_token},
            timeout=config.timeout_seconds,
            transport=transport,
        )

    def get_json(self, endpoint: str, params: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        for attempt in range(self.config.max_retries + 1):
            if self.limiter:
                self.limiter.acquire()
            try:
                response = self.client.get(endpoint, params=params)
            except httpx.RequestError as error:
                if attempt == self.config.max_retries:
                    raise ProviderResponseError("Falha de rede no provider.") from error
                self.sleeper(2**attempt)
                continue
            if response.status_code < 400:
                try:
                    data = response.json()
                except ValueError as error:
                    raise ProviderResponseError("JSON inválido recebido do provider.") from error
                if not isinstance(data, dict):
                    raise ProviderResponseError("Payload do provider deve ser um objeto JSON.")
                return data
            if response.status_code in {429, 500, 502, 503, 504} and attempt < self.config.max_retries:
                self.sleeper(float(response.headers.get("Retry-After", 2**attempt)))
                continue
            raise ProviderResponseError(f"Provider respondeu HTTP {response.status_code}.")
        raise AssertionError("Loop de retry terminou sem resultado.")  # pragma: no cover

    def close(self) -> None:
        self.client.close()


class FootballDataProvider:
    name = "football_data"
    capabilities = frozenset(ProviderCapability)

    def __init__(self, client: ProviderHTTPClient) -> None:
        self.client = client

    def fetch_competitions(self) -> Mapping[str, Any]:
        return self.client.get_json("/competitions")

    def fetch_teams(self, competition: str) -> Mapping[str, Any]:
        return self.client.get_json(f"/competitions/{competition}/teams")

    def fetch_matches(self, **filters: Any) -> Mapping[str, Any]:
        return self.client.get_json("/matches", filters)

    def fetch_standings(self, competition: str) -> Mapping[str, Any]:
        return self.client.get_json(f"/competitions/{competition}/standings")

    def health_check(self) -> ProviderHealth:
        started = time.monotonic()
        try:
            self.fetch_competitions()
            available, message = True, "Provider disponível."
        except ProviderError as error:
            available, message = False, str(error)
        return ProviderHealth(
            self.name,
            available,
            max(0, round((time.monotonic() - started) * 1000)),
            message,
            datetime.now(timezone.utc),
        )

    def close(self) -> None:
        self.client.close()


class ProviderCollector:
    def __init__(self, provider: FootballDataProvider, store: RawPayloadStore) -> None:
        self.provider, self.store = provider, store

    def collect(self, resource: str, **kwargs: Any) -> RawProviderPayload:
        operations = {
            "competitions": self.provider.fetch_competitions,
            "teams": self.provider.fetch_teams,
            "matches": self.provider.fetch_matches,
            "standings": self.provider.fetch_standings,
        }
        try:
            data = operations[resource](**kwargs)
        except KeyError as error:
            raise ValueError(f"Recurso desconhecido: {resource}.") from error
        payload = RawProviderPayload(
            self.provider.name,
            resource,
            str(kwargs.get("competition")) if kwargs.get("competition") else None,
            data,
            datetime.now(timezone.utc),
        )
        self.store.save(payload)
        return payload


class ProviderDashboard:
    def snapshot(
        self,
        providers: tuple[FootballDataProvider, ...],
        save: Callable[[ProviderHealth], None] | None = None,
    ) -> tuple[ProviderHealth, ...]:
        health = tuple(provider.health_check() for provider in providers)
        if save:
            for item in health:
                save(item)
        return health


class ProviderRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, Callable[[], FootballDataProvider]] = {}

    def register(
        self,
        name: str,
        factory: Callable[[], FootballDataProvider],
        *,
        replace: bool = False,
    ) -> None:
        normalized = name.strip().casefold()
        if not normalized:
            raise ValueError("Nome do provider é obrigatório.")
        if normalized in self._factories and not replace:
            raise ValueError(f"Provider já registrado: {normalized}.")
        self._factories[normalized] = factory

    def create(self, name: str) -> FootballDataProvider:
        normalized = name.strip().casefold()
        try:
            return self._factories[normalized]()
        except KeyError as error:
            raise LookupError(f"Provider desconhecido: {normalized}.") from error

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._factories))


def build_football_data_provider(
    config: ProviderConfig | None = None,
    *,
    transport: httpx.BaseTransport | None = None,
) -> FootballDataProvider:
    resolved = config or ProviderConfig.from_environment()
    limiter = RateLimiter(resolved.requests_per_minute)
    return FootballDataProvider(
        ProviderHTTPClient(resolved, transport=transport, limiter=limiter)
    )
