import base64
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json

import pytest

from ultrastats_ai.domain.operations import (
    APIRequest,
    APIRequestGuard,
    AuditEntry,
    BackupArtifact,
    CircuitBreaker,
    MetricsRegistry,
    PasswordHasher,
    Principal,
    QueueMessage,
    ReliableQueue,
    RetentionPolicy,
    SecretReference,
    SlidingWindowRateLimiter,
    TTLCache,
    TokenService,
    append_audit,
    authorize,
    create_backup,
    desired_replicas,
    operational_alerts,
    redact_secrets,
    restore_backup,
    review_dependencies,
    run_load_test,
    verify_audit,
)


NOW = datetime.now(timezone.utc)
SECRET = "x" * 32


def signed(payload):
    encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    ).rstrip(b"=").decode()
    signature = base64.urlsafe_b64encode(
        hmac.new(SECRET.encode(), encoded.encode(), hashlib.sha256).digest()
    ).rstrip(b"=").decode()
    return f"{encoded}.{signature}"


def test_token_authentication_and_authorization() -> None:
    service = TokenService(SECRET)
    token = service.issue("user", ("viewer", "admin", "viewer"), NOW)
    principal = service.verify(token, NOW)
    assert principal.subject == "user"
    assert principal.roles == ("admin", "viewer")
    assert authorize(principal, ("admin",))
    assert not authorize(principal, ("operator",))
    with pytest.raises(ValueError, match="papel"):
        authorize(principal, ())


@pytest.mark.parametrize(
    ("secret", "issuer"),
    [("short", "issuer"), (SECRET, "")],
)
def test_token_service_validation(secret, issuer) -> None:
    with pytest.raises(ValueError, match="segredo"):
        TokenService(secret, issuer)


@pytest.mark.parametrize(
    ("subject", "roles", "ttl"),
    [
        ("", ("admin",), timedelta(hours=1)),
        ("user", (), timedelta(hours=1)),
        ("user", ("admin",), timedelta(0)),
    ],
)
def test_token_issue_validation(subject, roles, ttl) -> None:
    with pytest.raises(ValueError, match="sujeito"):
        TokenService(SECRET).issue(subject, roles, NOW, ttl)


def test_token_rejects_signature_shape_issuer_expiry_and_claims() -> None:
    service = TokenService(SECRET)
    good = service.issue("user", ("admin",), NOW, timedelta(seconds=1))
    with pytest.raises(ValueError, match="Assinatura"):
        service.verify(good[:-1] + ("a" if good[-1] != "a" else "b"), NOW)
    with pytest.raises(ValueError, match="malformado"):
        service.verify("invalid", NOW)
    with pytest.raises(ValueError, match="Assinatura"):
        service.verify("%%%.abc", NOW)
    malformed_signature = base64.urlsafe_b64encode(
        hmac.new(SECRET.encode(), b"%%%", hashlib.sha256).digest()
    ).rstrip(b"=").decode()
    with pytest.raises(ValueError, match="malformado"):
        service.verify(f"%%%.{malformed_signature}", NOW)
    with pytest.raises(ValueError, match="Emissor"):
        service.verify(TokenService(SECRET, "other").issue("user", ("admin",), NOW), NOW)
    with pytest.raises(ValueError, match="expirado"):
        service.verify(good, NOW + timedelta(seconds=1))
    with pytest.raises(ValueError, match="Claims"):
        service.verify(signed({"iss": "ultrastats-ai", "sub": "user", "roles": []}), NOW)
    with pytest.raises(ValueError, match="Claims"):
        service.verify(
            signed({"iss": "ultrastats-ai", "exp": int((NOW + timedelta(hours=1)).timestamp()), "sub": "", "roles": "admin"}),
            NOW,
        )


def test_password_hash_and_verification() -> None:
    salt = b"0123456789abcdef"
    encoded = PasswordHasher.hash("a-secure-password", salt, 100_000)
    assert PasswordHasher.verify("a-secure-password", encoded)
    assert not PasswordHasher.verify("wrong-password", encoded)
    assert not PasswordHasher.verify("a-secure-password", "other$1$salt$digest")
    assert not PasswordHasher.verify("a-secure-password", "invalid")
    with pytest.raises(ValueError, match="insuficiente"):
        PasswordHasher.hash("short", salt)
    with pytest.raises(ValueError, match="insuficiente"):
        PasswordHasher.hash("a-secure-password", b"short")
    with pytest.raises(ValueError, match="insuficiente"):
        PasswordHasher.hash("a-secure-password", salt, 99_999)


def test_secret_references_resolution_and_redaction() -> None:
    reference = SecretReference("API_TOKEN")
    assert reference.resolve({"API_TOKEN": "secret"}) == "secret"
    with pytest.raises(ValueError, match="ausente"):
        reference.resolve({})
    for key in ("", "A=B", "A B", "A\nB"):
        with pytest.raises(ValueError, match="referência"):
            SecretReference(key)
    assert redact_secrets("token=secret", ("secret", "")) == "token=[REDACTED]"


def test_rate_limiter_window_and_validation() -> None:
    limiter = SlidingWindowRateLimiter(2, timedelta(seconds=10))
    assert limiter.allow("client", NOW)
    assert limiter.allow("client", NOW)
    assert not limiter.allow("client", NOW)
    assert limiter.allow("client", NOW + timedelta(seconds=11))
    with pytest.raises(ValueError, match="máximo"):
        SlidingWindowRateLimiter(0, timedelta(seconds=1))
    with pytest.raises(ValueError, match="máximo"):
        SlidingWindowRateLimiter(1, timedelta(0))
    with pytest.raises(ValueError, match="chave"):
        limiter.allow("", NOW)


def test_api_security_guard_all_controls() -> None:
    limiter = SlidingWindowRateLimiter(1, timedelta(minutes=1))
    guard = APIRequestGuard(limiter, ("https://app.test",), 100)
    valid = APIRequest("client", True, 10, "application/json", "https://app.test")
    assert guard.validate(valid, NOW) == ()
    invalid = APIRequest("client", False, 101, "text/plain", "https://evil.test")
    assert guard.validate(invalid, NOW) == (
        "https_required",
        "invalid_content_length",
        "unsupported_content_type",
        "origin_denied",
        "rate_limited",
    )
    negative = APIRequest("other", True, -1, "application/problem+json", "https://app.test")
    assert guard.validate(negative, NOW) == ("invalid_content_length",)
    with pytest.raises(ValueError, match="origens"):
        APIRequestGuard(limiter, ())
    with pytest.raises(ValueError, match="limite"):
        APIRequestGuard(limiter, ("x",), 0)


def test_ttl_cache_hit_miss_expiry_eviction_and_update() -> None:
    cache = TTLCache(2)
    assert cache.get("missing", NOW) is None
    cache.set("a", 1, NOW + timedelta(seconds=1))
    cache.set("b", 2, NOW + timedelta(seconds=2))
    assert cache.get("a", NOW) == 1
    cache.set("a", 3, NOW + timedelta(seconds=3))
    cache.set("c", 4, NOW + timedelta(seconds=4))
    assert cache.get("b", NOW) is None
    assert cache.get("a", NOW) == 3
    assert cache.get("a", NOW + timedelta(seconds=3)) is None
    with pytest.raises(ValueError, match="capacidade"):
        TTLCache(0)
    with pytest.raises(ValueError, match="chave"):
        cache.set("", 1, NOW)


def test_reliable_queue_ack_retry_dead_letter_and_idempotency() -> None:
    queue = ReliableQueue(2)
    message = QueueMessage("id", {"value": 1})
    assert queue.publish(message)
    assert not queue.publish(message)
    consumed = queue.consume()
    assert consumed.attempts == 1
    assert not queue.ack("missing")
    assert queue.nack("id")
    consumed = queue.consume()
    assert consumed.attempts == 2
    assert queue.nack("id")
    assert queue.dead_letters == [consumed]
    assert queue.consume() is None
    assert not queue.nack("missing")
    assert queue.publish(QueueMessage("ack", {}))
    queue.consume()
    assert queue.ack("ack")
    with pytest.raises(ValueError, match="tentativas"):
        ReliableQueue(0)
    with pytest.raises(ValueError, match="identidade"):
        queue.publish(QueueMessage("", {}))


def test_circuit_breaker_transitions() -> None:
    breaker = CircuitBreaker(2, timedelta(seconds=10))
    assert breaker.allow(NOW)
    breaker = breaker.failure(NOW)
    assert breaker.opened_at is None
    breaker = breaker.failure(NOW)
    assert not breaker.allow(NOW + timedelta(seconds=9))
    assert breaker.allow(NOW + timedelta(seconds=10))
    assert breaker.success().failures == 0
    with pytest.raises(ValueError, match="limites"):
        CircuitBreaker(0)
    with pytest.raises(ValueError, match="limites"):
        CircuitBreaker(1, timedelta(0))


def test_backup_checksum_recovery_and_corruption() -> None:
    artifact = create_backup({"b": 2, "a": 1}, NOW)
    assert restore_backup(artifact) == {"a": 1, "b": 2}
    with pytest.raises(ValueError, match="Checksum"):
        restore_backup(replace(artifact, payload=b"corrupt"))
    list_payload = json.dumps([1]).encode()
    list_artifact = BackupArtifact(list_payload, hashlib.sha256(list_payload).hexdigest(), NOW)
    with pytest.raises(ValueError, match="objeto"):
        restore_backup(list_artifact)


def test_hash_chained_audit_and_tampering() -> None:
    entries = append_audit((), "login", "user", NOW)
    entries = append_audit(entries, "update", "user", NOW + timedelta(seconds=1))
    assert verify_audit(entries)
    assert not verify_audit((replace(entries[0], action="tampered"), entries[1]))
    assert not verify_audit((replace(entries[0], sequence=2),))
    assert not verify_audit((replace(entries[0], previous_hash="bad"),))
    with pytest.raises(ValueError, match="ação"):
        append_audit((), "", "user", NOW)
    with pytest.raises(ValueError, match="ator"):
        append_audit((), "login", "", NOW)


def test_metrics_registry_and_operational_alerts() -> None:
    registry = MetricsRegistry()
    registry.increment("requests")
    registry.increment("requests", 2)
    registry.gauge("workers", 3)
    registry.observe("latency", .1)
    registry.observe("latency", .3)
    snapshot = registry.snapshot()
    assert snapshot["counters"]["requests"] == 3
    assert snapshot["gauges"]["workers"] == 3
    assert snapshot["histograms"]["latency"] == {
        "count": 2,
        "average": .2,
        "maximum": .3,
    }
    assert operational_alerts({"error_rate": .2, "latency": 1}, {"error_rate": .1, "missing": 1}) == ("error_rate",)
    with pytest.raises(ValueError, match="Contador"):
        registry.increment("", 1)
    with pytest.raises(ValueError, match="incremento"):
        registry.increment("x", -1)
    with pytest.raises(ValueError, match="Gauge"):
        registry.gauge("", 1)
    with pytest.raises(ValueError, match="Histograma"):
        registry.observe("", 1)
    with pytest.raises(ValueError, match="valor"):
        registry.observe("x", -1)


def test_retention_and_scaling() -> None:
    policy = RetentionPolicy({"audit": timedelta(days=365)})
    assert not policy.expired("audit", NOW, NOW + timedelta(days=364))
    assert policy.expired("audit", NOW, NOW + timedelta(days=365))
    with pytest.raises(ValueError, match="Categoria"):
        policy.expired("unknown", NOW, NOW)
    with pytest.raises(ValueError, match="durações"):
        RetentionPolicy({})
    with pytest.raises(ValueError, match="durações"):
        RetentionPolicy({"x": timedelta(0)})
    assert desired_replicas(0, 100, 2, 10) == 2
    assert desired_replicas(250, 100, 1, 10) == 3
    assert desired_replicas(2000, 100, 1, 10) == 10
    for values in ((-1, 1, 1, 2), (1, 0, 1, 2), (1, 1, 0, 2), (1, 1, 3, 2)):
        with pytest.raises(ValueError, match="escalabilidade"):
            desired_replicas(*values)


def test_load_testing_and_dependency_review() -> None:
    calls = 0

    def handler():
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("failure")

    result = run_load_test(handler, 3)
    assert result.requests == 3 and result.failures == 1
    assert result.maximum_seconds >= result.average_seconds >= 0
    with pytest.raises(ValueError, match="requisições"):
        run_load_test(handler, 0)
    findings = review_dependencies(
        {"safe": "2.0", "old": "1.2", "bad": "1.0"},
        ("bad",),
        {"old": "1.3", "safe": "1.0"},
    )
    assert findings == ("blocked:bad", "outdated:old")
    with pytest.raises(ValueError, match="Versão"):
        review_dependencies({"bad-version": "x"}, (), {"bad-version": "1"})
