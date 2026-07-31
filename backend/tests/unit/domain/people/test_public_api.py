"""Testes da API pública inicial do People Context."""

import ultrastats_ai.domain.people as people


EXPECTED_EXPORTS = {
    "Coach",
    "CoachRole",
    "CoachStatus",
    "DuplicatePersonAliasError",
    "InvalidProfessionalPeriodError",
    "InvalidRetirementStateError",
    "PeopleDomainError",
    "PeopleHistoryAction",
    "PeopleProfileType",
    "Person",
    "PersonAliasNotFoundError",
    "PersonAliases",
    "PersonAlreadyActiveError",
    "PersonAlreadyInactiveError",
    "PersonHistoryEntry",
    "PersonNameAliasConflictError",
    "PersonProfileAlreadyExistsError",
    "PersonProfileNotFoundError",
    "PersonProfileOwnershipError",
    "Player",
    "PlayerStatus",
    "Referee",
    "RefereeCategory",
    "RefereeRole",
    "RefereeStatus",
}

def test_people_public_api_exports_expected_symbols() -> None:
    assert set(people.__all__) == EXPECTED_EXPORTS


def test_people_public_api_symbols_are_available() -> None:
    for symbol in EXPECTED_EXPORTS:
        assert hasattr(people, symbol)