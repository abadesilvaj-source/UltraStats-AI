"""Testes da hierarquia de erros de Competition."""

import pytest

from ultrastats_ai.domain.competition import (
    AliasNotFoundError,
    CompetitionDomainError,
    CompetitionHierarchyError,
    DuplicateAliasError,
    DuplicateHistoryFieldError,
    DuplicateTieMatchError,
    DuplicateTieMatchSequenceError,
    EmptyHistoryChangesError,
    InvalidSeasonTransitionError,
    NameAliasConflictError,
)
from ultrastats_ai.domain.shared import (
    InvariantViolationError,
)


@pytest.mark.parametrize(
    "error_type",
    [
        DuplicateAliasError,
        AliasNotFoundError,
        NameAliasConflictError,
        InvalidSeasonTransitionError,
        CompetitionHierarchyError,
        DuplicateTieMatchError,
        DuplicateTieMatchSequenceError,
        DuplicateHistoryFieldError,
        EmptyHistoryChangesError,
    ],
)
def test_specific_errors_inherit_from_competition_error(
    error_type: type[Exception],
) -> None:
    assert issubclass(
        error_type,
        CompetitionDomainError,
    )


def test_competition_error_inherits_from_invariant_error() -> None:
    assert issubclass(
        CompetitionDomainError,
        InvariantViolationError,
    )


@pytest.mark.parametrize(
    ("error_type", "message"),
    [
        (
            DuplicateAliasError,
            "Alias duplicado.",
        ),
        (
            AliasNotFoundError,
            "Alias não encontrado.",
        ),
        (
            NameAliasConflictError,
            "Conflito entre nome e alias.",
        ),
        (
            InvalidSeasonTransitionError,
            "Transição inválida.",
        ),
        (
            CompetitionHierarchyError,
            "Hierarquia inválida.",
        ),
        (
            DuplicateTieMatchError,
            "Partida duplicada.",
        ),
        (
            DuplicateTieMatchSequenceError,
            "Sequência duplicada.",
        ),
        (
            DuplicateHistoryFieldError,
            "Campo duplicado.",
        ),
        (
            EmptyHistoryChangesError,
            "Alterações vazias.",
        ),
    ],
)
def test_errors_preserve_message(
    error_type: type[Exception],
    message: str,
) -> None:
    error = error_type(message)

    assert str(error) == message