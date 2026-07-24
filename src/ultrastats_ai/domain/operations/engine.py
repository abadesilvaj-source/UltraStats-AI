"""Primitivas determinísticas de segurança, resiliência e operação."""

from __future__ import annotations

import base64
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from time import perf_counter
from typing import Callable, Mapping


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


@dataclass(frozen=True, slots=True)
class Principal:
    subject: str
    roles: tuple[str, ...]
    expires_at: datetime


class TokenService:
    def __init__(self, secret: str, issuer: str = "ultrastats-ai") -> None:
        if len(secret) < 32 or not issuer.strip():
            raise ValueError("Token exige segredo forte e emissor.")
        self._secret = secret.encode()
        self.issuer = issuer

    def issue(
        self,
        subject: str,
        roles: tuple[str, ...],
        now: datetime,
        ttl: timedelta = timedelta(hours=1),
    ) -> str:
        if not subject.strip() or not roles or ttl <= timedelta(0):
            raise ValueError("Token exige sujeito, papéis e validade.")
        payload = {
            "iss": self.issuer,
            "sub": subject,
            "roles": sorted(set(roles)),
            "exp": int((now + ttl).timestamp()),
        }
        encoded = _b64(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
        signature = _b64(hmac.new(self._secret, encoded.encode(), hashlib.sha256).digest())
        return f"{encoded}.{signature}"

    def verify(self, token: str, now: datetime) -> Principal:
        parts = token.split(".")
        if len(parts) != 2:
            raise ValueError("Token malformado.")
        encoded, signature = parts
        expected = _b64(hmac.new(self._secret, encoded.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Assinatura de token inválida.")
        try:
            payload = json.loads(_unb64(encoded))
        except Exception as error:
            raise ValueError("Token malformado.") from error
        if payload.get("iss") != self.issuer:
            raise ValueError("Emissor de token inválido.")
        try:
            expires_at = datetime.fromtimestamp(payload["exp"], timezone.utc)
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Claims de token inválidos.") from error
        if now >= expires_at:
            raise ValueError("Token expirado.")
        subject, roles = payload.get("sub"), payload.get("roles")
        if not isinstance(subject, str) or not subject or not isinstance(roles, list):
            raise ValueError("Claims de token inválidos.")
        return Principal(subject, tuple(str(role) for role in roles), expires_at)


class PasswordHasher:
    @staticmethod
    def hash(password: str, salt: bytes, iterations: int = 200_000) -> str:
        if len(password) < 12 or len(salt) < 16 or iterations < 100_000:
            raise ValueError("Senha, salt ou custo insuficiente.")
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
        return f"pbkdf2_sha256${iterations}${_b64(salt)}${_b64(digest)}"

    @staticmethod
    def verify(password: str, encoded: str) -> bool:
        try:
            algorithm, iterations, salt, digest = encoded.split("$")
            if algorithm != "pbkdf2_sha256":
                return False
            candidate = PasswordHasher.hash(password, _unb64(salt), int(iterations))
            return hmac.compare_digest(candidate, encoded)
        except (ValueError, TypeError):
            return False


def authorize(principal: Principal, required_roles: tuple[str, ...]) -> bool:
    if not required_roles:
        raise ValueError("Autorização exige ao menos um papel.")
    return bool(set(principal.roles).intersection(required_roles))


@dataclass(frozen=True, slots=True)
class SecretReference:
    environment_key: str

    def __post_init__(self) -> None:
        if not self.environment_key.strip() or any(
            marker in self.environment_key for marker in ("=", " ", "\n")
        ):
            raise ValueError("Credencial deve ser uma referência de ambiente.")

    def resolve(self, environment: Mapping[str, str]) -> str:
        value = environment.get(self.environment_key, "")
        if not value:
            raise ValueError("Credencial obrigatória ausente.")
        return value


def redact_secrets(message: str, secrets: tuple[str, ...]) -> str:
    redacted = message
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    return redacted


class SlidingWindowRateLimiter:
    def __init__(self, maximum: int, window: timedelta) -> None:
        if maximum <= 0 or window <= timedelta(0):
            raise ValueError("Rate limit exige máximo e janela positivos.")
        self.maximum, self.window = maximum, window
        self._requests: dict[str, list[datetime]] = {}

    def allow(self, key: str, now: datetime) -> bool:
        if not key.strip():
            raise ValueError("Rate limit exige chave.")
        threshold = now - self.window
        active = [value for value in self._requests.get(key, []) if value > threshold]
        if len(active) >= self.maximum:
            self._requests[key] = active
            return False
        active.append(now)
        self._requests[key] = active
        return True


@dataclass(frozen=True, slots=True)
class APIRequest:
    client_id: str
    secure: bool
    content_length: int
    content_type: str
    origin: str


class APIRequestGuard:
    def __init__(
        self,
        limiter: SlidingWindowRateLimiter,
        allowed_origins: tuple[str, ...],
        maximum_body_bytes: int = 1_000_000,
    ) -> None:
        if not allowed_origins or maximum_body_bytes <= 0:
            raise ValueError("Guarda de API exige origens e limite.")
        self.limiter = limiter
        self.allowed_origins = allowed_origins
        self.maximum_body_bytes = maximum_body_bytes

    def validate(self, request: APIRequest, now: datetime) -> tuple[str, ...]:
        violations = []
        if not request.secure:
            violations.append("https_required")
        if request.content_length < 0 or request.content_length > self.maximum_body_bytes:
            violations.append("invalid_content_length")
        if request.content_type not in {"application/json", "application/problem+json"}:
            violations.append("unsupported_content_type")
        if request.origin not in self.allowed_origins:
            violations.append("origin_denied")
        if not self.limiter.allow(request.client_id, now):
            violations.append("rate_limited")
        return tuple(violations)


class TTLCache:
    def __init__(self, maximum_entries: int) -> None:
        if maximum_entries <= 0:
            raise ValueError("Cache exige capacidade positiva.")
        self.maximum_entries = maximum_entries
        self._values: dict[str, tuple[object, datetime]] = {}

    def set(self, key: str, value: object, expires_at: datetime) -> None:
        if not key.strip():
            raise ValueError("Cache exige chave.")
        if key not in self._values and len(self._values) >= self.maximum_entries:
            oldest = min(self._values, key=lambda item: self._values[item][1])
            del self._values[oldest]
        self._values[key] = (value, expires_at)

    def get(self, key: str, now: datetime) -> object | None:
        item = self._values.get(key)
        if item is None:
            return None
        value, expires_at = item
        if now >= expires_at:
            del self._values[key]
            return None
        return value


@dataclass(frozen=True, slots=True)
class QueueMessage:
    message_id: str
    payload: Mapping[str, object]
    attempts: int = 0


class ReliableQueue:
    def __init__(self, maximum_attempts: int = 3) -> None:
        if maximum_attempts <= 0:
            raise ValueError("Fila exige tentativas positivas.")
        self.maximum_attempts = maximum_attempts
        self._ready: list[QueueMessage] = []
        self._inflight: dict[str, QueueMessage] = {}
        self.dead_letters: list[QueueMessage] = []
        self._known: set[str] = set()

    def publish(self, message: QueueMessage) -> bool:
        if not message.message_id.strip():
            raise ValueError("Mensagem exige identidade.")
        if message.message_id in self._known:
            return False
        self._known.add(message.message_id)
        self._ready.append(message)
        return True

    def consume(self) -> QueueMessage | None:
        if not self._ready:
            return None
        message = self._ready.pop(0)
        attempted = replace(message, attempts=message.attempts + 1)
        self._inflight[attempted.message_id] = attempted
        return attempted

    def ack(self, message_id: str) -> bool:
        return self._inflight.pop(message_id, None) is not None

    def nack(self, message_id: str) -> bool:
        message = self._inflight.pop(message_id, None)
        if message is None:
            return False
        if message.attempts >= self.maximum_attempts:
            self.dead_letters.append(message)
        else:
            self._ready.append(message)
        return True


@dataclass(frozen=True, slots=True)
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_timeout: timedelta = timedelta(seconds=30)
    failures: int = 0
    opened_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.failure_threshold <= 0 or self.recovery_timeout <= timedelta(0):
            raise ValueError("Circuit breaker exige limites positivos.")

    def allow(self, now: datetime) -> bool:
        return self.opened_at is None or now - self.opened_at >= self.recovery_timeout

    def success(self) -> CircuitBreaker:
        return replace(self, failures=0, opened_at=None)

    def failure(self, now: datetime) -> CircuitBreaker:
        failures = self.failures + 1
        return replace(
            self,
            failures=failures,
            opened_at=now if failures >= self.failure_threshold else self.opened_at,
        )


@dataclass(frozen=True, slots=True)
class BackupArtifact:
    payload: bytes
    checksum: str
    created_at: datetime


def create_backup(data: Mapping[str, object], created_at: datetime) -> BackupArtifact:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return BackupArtifact(payload, hashlib.sha256(payload).hexdigest(), created_at)


def restore_backup(artifact: BackupArtifact) -> Mapping[str, object]:
    if not hmac.compare_digest(hashlib.sha256(artifact.payload).hexdigest(), artifact.checksum):
        raise ValueError("Checksum de backup inválido.")
    value = json.loads(artifact.payload)
    if not isinstance(value, dict):
        raise ValueError("Backup deve conter um objeto.")
    return value


@dataclass(frozen=True, slots=True)
class AuditEntry:
    sequence: int
    action: str
    actor: str
    occurred_at: datetime
    previous_hash: str
    hash: str


def append_audit(
    entries: tuple[AuditEntry, ...],
    action: str,
    actor: str,
    occurred_at: datetime,
) -> tuple[AuditEntry, ...]:
    if not action.strip() or not actor.strip():
        raise ValueError("Auditoria exige ação e ator.")
    previous = entries[-1].hash if entries else "GENESIS"
    sequence = len(entries) + 1
    content = f"{sequence}|{action}|{actor}|{occurred_at.isoformat()}|{previous}"
    digest = hashlib.sha256(content.encode()).hexdigest()
    return (*entries, AuditEntry(sequence, action, actor, occurred_at, previous, digest))


def verify_audit(entries: tuple[AuditEntry, ...]) -> bool:
    previous = "GENESIS"
    for index, entry in enumerate(entries, 1):
        content = (
            f"{entry.sequence}|{entry.action}|{entry.actor}|"
            f"{entry.occurred_at.isoformat()}|{entry.previous_hash}"
        )
        if (
            entry.sequence != index
            or entry.previous_hash != previous
            or hashlib.sha256(content.encode()).hexdigest() != entry.hash
        ):
            return False
        previous = entry.hash
    return True


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._samples: dict[str, list[float]] = {}

    def increment(self, name: str, amount: int = 1) -> None:
        if not name.strip() or amount < 0:
            raise ValueError("Contador exige nome e incremento não negativo.")
        self._counters[name] = self._counters.get(name, 0) + amount

    def gauge(self, name: str, value: float) -> None:
        if not name.strip():
            raise ValueError("Gauge exige nome.")
        self._gauges[name] = value

    def observe(self, name: str, value: float) -> None:
        if not name.strip() or value < 0:
            raise ValueError("Histograma exige nome e valor não negativo.")
        self._samples.setdefault(name, []).append(value)

    def snapshot(self) -> dict[str, object]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                name: {
                    "count": len(values),
                    "average": sum(values) / len(values),
                    "maximum": max(values),
                }
                for name, values in self._samples.items()
            },
        }


def operational_alerts(
    metrics: Mapping[str, float],
    maximums: Mapping[str, float],
) -> tuple[str, ...]:
    return tuple(
        sorted(
            name
            for name, maximum in maximums.items()
            if name in metrics and metrics[name] > maximum
        )
    )


@dataclass(frozen=True, slots=True)
class RetentionPolicy:
    durations: Mapping[str, timedelta]

    def __post_init__(self) -> None:
        if not self.durations or any(value <= timedelta(0) for value in self.durations.values()):
            raise ValueError("Retenção exige durações positivas.")

    def expired(self, category: str, created_at: datetime, now: datetime) -> bool:
        if category not in self.durations:
            raise ValueError("Categoria sem política de retenção.")
        return now - created_at >= self.durations[category]


def desired_replicas(
    requests_per_second: float,
    capacity_per_replica: float,
    minimum: int,
    maximum: int,
) -> int:
    if requests_per_second < 0 or capacity_per_replica <= 0 or minimum <= 0 or maximum < minimum:
        raise ValueError("Parâmetros de escalabilidade inválidos.")
    required = int(-(-requests_per_second // capacity_per_replica))
    return max(minimum, min(maximum, required or minimum))


@dataclass(frozen=True, slots=True)
class LoadTestResult:
    requests: int
    failures: int
    average_seconds: float
    maximum_seconds: float


def run_load_test(handler: Callable[[], object], requests: int) -> LoadTestResult:
    if requests <= 0:
        raise ValueError("Teste de carga exige requisições.")
    failures = 0
    durations = []
    for _ in range(requests):
        started = perf_counter()
        try:
            handler()
        except Exception:
            failures += 1
        durations.append(perf_counter() - started)
    return LoadTestResult(
        requests,
        failures,
        sum(durations) / len(durations),
        max(durations),
    )


def review_dependencies(
    installed: Mapping[str, str],
    blocked: tuple[str, ...],
    minimum_versions: Mapping[str, str],
) -> tuple[str, ...]:
    findings = []
    for package in sorted(installed):
        if package in blocked:
            findings.append(f"blocked:{package}")
        minimum = minimum_versions.get(package)
        if minimum is not None and _version(installed[package]) < _version(minimum):
            findings.append(f"outdated:{package}")
    return tuple(findings)


def _version(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in value.split("."))
    except ValueError as error:
        raise ValueError("Versão de dependência inválida.") from error
