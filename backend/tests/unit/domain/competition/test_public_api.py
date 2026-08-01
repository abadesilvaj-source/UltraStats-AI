"""Testes da API pública do contexto Competition."""

import ultrastats_ai.domain.competition as competition_domain


EXPECTED_PUBLIC_NAMES = {
    "AliasNotFoundError",
    "Competition",
    "CompetitionAliases",
    "CompetitionChangeType",
    "CompetitionDomainError",
    "CompetitionEntityKind",
    "CompetitionFieldChange",
    "CompetitionHierarchyError",
    "CompetitionHistoryEntry",
    "CompetitionHistoryRepository",
    "CompetitionReconstruction",
    "CompetitionRepository",
    "DuplicateAliasError",
    "DuplicateHistoryFieldError",
    "DuplicateTieMatchError",
    "DuplicateTieMatchSequenceError",
    "EmptyHistoryChangesError",
    "InvalidSeasonTransitionError",
    "NameAliasConflictError",
    "Round",
    "RoundReconstruction",
    "Season",
    "SeasonReconstruction",
    "SeasonRepository",
    "Stage",
    "StageReconstruction",
    "Tie",
    "TieMatchReference",
    "TieReconstruction",
    "TieRepository",
}


def test_public_api_exports_expected_names() -> None:
    assert set(competition_domain.__all__) == (
        EXPECTED_PUBLIC_NAMES
    )


def test_every_public_name_is_importable() -> None:
    for name in competition_domain.__all__:
        assert hasattr(competition_domain, name)


def test_public_api_does_not_contain_duplicates() -> None:
    assert len(competition_domain.__all__) == len(
        set(competition_domain.__all__)
    )