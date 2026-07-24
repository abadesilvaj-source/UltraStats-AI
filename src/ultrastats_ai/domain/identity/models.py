"""Modelo de resolução de identidade, revisão e quarentena."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from difflib import SequenceMatcher
import re
import unicodedata
from typing import Mapping


class ResolutionStatus(StrEnum):
    MATCHED = "matched"
    REVIEW = "review"
    UNMATCHED = "unmatched"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class NormalizedIdentity:
    name: str
    country: str | None = None


class IdentityNormalizer:
    def normalize(self, name: str, country: str | None = None) -> NormalizedIdentity:
        normalized = self._text(name)
        if not normalized:
            raise ValueError("Nome normalizado não pode ser vazio.")
        return NormalizedIdentity(normalized, self._text(country) if country else None)

    @staticmethod
    def _text(value: str) -> str:
        ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
        return re.sub(r"[^a-z0-9]+", " ", ascii_value.casefold()).strip()


@dataclass(frozen=True, slots=True)
class IdentityCandidate:
    canonical_id: str
    score: Decimal
    evidence: Mapping[str, Decimal]

    def __post_init__(self) -> None:
        if not self.canonical_id.strip() or not Decimal("0") <= self.score <= Decimal("1"):
            raise ValueError("Candidato de identidade inválido.")


@dataclass(frozen=True, slots=True)
class IdentityDecision:
    provider: str
    external_id: str
    status: ResolutionStatus
    decided_at: datetime
    candidate: IdentityCandidate | None = None
    reason: str = ""
    reviewer: str | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.external_id.strip() or not self.reason.strip():
            raise ValueError("Decisão exige provider, identidade e justificativa.")
        if self.status is ResolutionStatus.MATCHED and self.candidate is None:
            raise ValueError("Decisão matched exige candidato.")

    def review(self, accepted: bool, reviewer: str, reason: str) -> IdentityDecision:
        if self.status is not ResolutionStatus.REVIEW:
            raise ValueError("Somente decisões pendentes aceitam revisão.")
        if not reviewer.strip() or not reason.strip():
            raise ValueError("Revisão exige responsável e justificativa.")
        status = ResolutionStatus.MATCHED if accepted else ResolutionStatus.REJECTED
        return replace(self, status=status, reviewer=reviewer, reason=reason)


@dataclass(frozen=True, slots=True)
class QuarantinedData:
    provider: str
    resource: str
    payload_fingerprint: str
    reason: str
    quarantined_at: datetime
    attempts: int = 0

    def __post_init__(self) -> None:
        if not all((self.provider.strip(), self.resource.strip(), self.payload_fingerprint.strip(), self.reason.strip())):
            raise ValueError("Quarentena exige origem, fingerprint e motivo.")
        if self.attempts < 0:
            raise ValueError("Tentativas não podem ser negativas.")

    def reprocess(self) -> QuarantinedData:
        return replace(self, attempts=self.attempts + 1)


class IdentityResolutionEngine:
    def __init__(
        self,
        *,
        auto_threshold: Decimal = Decimal("0.95"),
        review_threshold: Decimal = Decimal("0.70"),
    ) -> None:
        if not Decimal("0") <= review_threshold <= auto_threshold <= Decimal("1"):
            raise ValueError("Thresholds de identidade inválidos.")
        self.auto_threshold = auto_threshold
        self.review_threshold = review_threshold

    def candidates(
        self,
        incoming: NormalizedIdentity,
        canonical: Mapping[str, tuple[NormalizedIdentity, ...]],
    ) -> tuple[IdentityCandidate, ...]:
        result = []
        for canonical_id, aliases in canonical.items():
            score = max(self._score(incoming, alias) for alias in aliases)
            result.append(IdentityCandidate(canonical_id, score, {"similarity": score}))
        return tuple(sorted(result, key=lambda item: (-item.score, item.canonical_id)))

    def decide(
        self,
        provider: str,
        external_id: str,
        candidates: tuple[IdentityCandidate, ...],
        decided_at: datetime,
    ) -> IdentityDecision:
        candidate = candidates[0] if candidates else None
        score = candidate.score if candidate else Decimal("0")
        if score >= self.auto_threshold:
            status, reason = ResolutionStatus.MATCHED, "auto_threshold"
        elif score >= self.review_threshold:
            status, reason = ResolutionStatus.REVIEW, "manual_review_threshold"
        else:
            status, reason, candidate = ResolutionStatus.UNMATCHED, "below_threshold", None
        return IdentityDecision(provider, external_id, status, decided_at, candidate, reason)

    @staticmethod
    def _score(left: NormalizedIdentity, right: NormalizedIdentity) -> Decimal:
        name = Decimal(str(SequenceMatcher(None, left.name, right.name).ratio()))
        if left.country and right.country:
            country = Decimal("1") if left.country == right.country else Decimal("0")
            return name * Decimal("0.85") + country * Decimal("0.15")
        return name
