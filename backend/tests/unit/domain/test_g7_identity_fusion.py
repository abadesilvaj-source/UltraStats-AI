from datetime import datetime, timezone
from decimal import Decimal as D

import pytest

from ultrastats_ai.domain.data_fusion import (
    DataFusionEngine,
    ProviderObservation,
)
from ultrastats_ai.domain.identity import (
    IdentityCandidate,
    IdentityDecision,
    IdentityNormalizer,
    IdentityResolutionEngine,
    NormalizedIdentity,
    QuarantinedData,
    ResolutionStatus,
)
from ultrastats_ai.domain.policies import ProviderPriorityPolicy


NOW = datetime.now(timezone.utc)


def test_normalization_candidates_and_threshold_validation() -> None:
    normalizer = IdentityNormalizer()
    assert normalizer.normalize("  São   Paulo FC ", "Brasil") == NormalizedIdentity(
        "sao paulo fc", "brasil"
    )
    assert normalizer.normalize("Ajax").country is None
    with pytest.raises(ValueError, match="vazio"):
        normalizer.normalize(" -- ")
    with pytest.raises(ValueError, match="Thresholds"):
        IdentityResolutionEngine(auto_threshold=D(".5"), review_threshold=D(".6"))
    engine = IdentityResolutionEngine()
    candidates = engine.candidates(
        normalizer.normalize("Sao Paulo FC", "Brasil"),
        {
            "2": (normalizer.normalize("Palmeiras", "Brasil"),),
            "1": (
                normalizer.normalize("São Paulo", "Brazil"),
                normalizer.normalize("Sao Paulo FC", "Brasil"),
            ),
        },
    )
    assert candidates[0].canonical_id == "1"
    assert candidates[0].score == 1


def test_candidates_without_country_and_invalid_candidate() -> None:
    engine = IdentityResolutionEngine()
    candidates = engine.candidates(
        NormalizedIdentity("benfica"),
        {"club": (NormalizedIdentity("benfica"),)},
    )
    assert candidates[0].score == 1
    for candidate_id, score in (("", D(".5")), ("x", D("-1")), ("x", D("1.1"))):
        with pytest.raises(ValueError, match="inválido"):
            IdentityCandidate(candidate_id, score, {})


@pytest.mark.parametrize(
    ("score", "status", "has_candidate"),
    [
        (D(".96"), ResolutionStatus.MATCHED, True),
        (D(".80"), ResolutionStatus.REVIEW, True),
        (D(".20"), ResolutionStatus.UNMATCHED, False),
    ],
)
def test_resolution_decisions(score, status, has_candidate) -> None:
    candidate = IdentityCandidate("team-1", score, {"name": score})
    decision = IdentityResolutionEngine().decide("provider", "42", (candidate,), NOW)
    assert decision.status is status
    assert (decision.candidate is not None) is has_candidate
    empty = IdentityResolutionEngine().decide("provider", "43", (), NOW)
    assert empty.status is ResolutionStatus.UNMATCHED


def test_decision_invariants_and_manual_review() -> None:
    candidate = IdentityCandidate("team-1", D(".8"), {})
    with pytest.raises(ValueError, match="provider"):
        IdentityDecision("", "1", ResolutionStatus.REVIEW, NOW, candidate, "reason")
    with pytest.raises(ValueError, match="candidato"):
        IdentityDecision("p", "1", ResolutionStatus.MATCHED, NOW, None, "reason")
    pending = IdentityDecision(
        "p", "1", ResolutionStatus.REVIEW, NOW, candidate, "threshold"
    )
    assert pending.review(True, "ana", "confirmed").status is ResolutionStatus.MATCHED
    assert pending.review(False, "ana", "wrong").status is ResolutionStatus.REJECTED
    with pytest.raises(ValueError, match="responsável"):
        pending.review(True, "", "")
    matched = pending.review(True, "ana", "confirmed")
    with pytest.raises(ValueError, match="pendentes"):
        matched.review(True, "ana", "again")


def test_quarantine_and_reprocessing() -> None:
    quarantine = QuarantinedData("p", "teams", "hash", "invalid", NOW)
    assert quarantine.reprocess().attempts == 1
    with pytest.raises(ValueError, match="Quarentena"):
        QuarantinedData("", "teams", "hash", "invalid", NOW)
    with pytest.raises(ValueError, match="Tentativas"):
        QuarantinedData("p", "teams", "hash", "invalid", NOW, -1)


def test_data_fusion_priority_conflicts_nulls_and_traceability() -> None:
    first = ProviderObservation(
        "preferred",
        "team-1",
        {"name": "São Paulo", "country": "BR", "empty": None},
        NOW,
        "hash-1",
    )
    second = ProviderObservation(
        "other",
        "team-1",
        {"name": "Sao Paulo", "country": "BR"},
        NOW,
        "hash-2",
    )
    engine = DataFusionEngine(ProviderPriorityPolicy({"preferred": 1, "other": 2}))
    result = engine.fuse((second, first), NOW)
    assert result.values == {"country": "BR", "name": "São Paulo"}
    assert result.provenance["name"] == "preferred"
    assert len(result.conflicts) == 1
    assert result.conflicts[0].values["other"] == "Sao Paulo"
    with pytest.raises(ValueError, match="observações"):
        engine.fuse((), NOW)
    different = ProviderObservation("other", "team-2", {}, NOW, "hash")
    with pytest.raises(ValueError, match="diferentes"):
        engine.fuse((first, different), NOW)
    with pytest.raises(ValueError, match="rastreabilidade"):
        ProviderObservation("", "team", {}, NOW, "hash")
