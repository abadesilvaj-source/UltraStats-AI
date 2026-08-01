"""Testes da entidade TieMatchReference."""

from dataclasses import FrozenInstanceError

import pytest

from ultrastats_ai.domain.competition import (
    TieMatchReference,
)
from ultrastats_ai.domain.shared import MatchId


def test_tie_match_reference_is_created() -> None:
    match_id = MatchId.new()

    reference = TieMatchReference(
        match_id=match_id,
        sequence=1,
    )

    assert reference.match_id == match_id
    assert reference.sequence == 1


@pytest.mark.parametrize(
    "sequence",
    [
        1,
        2,
        10,
    ],
)
def test_tie_match_reference_accepts_positive_sequence(
    sequence: int,
) -> None:
    reference = TieMatchReference(
        match_id=MatchId.new(),
        sequence=sequence,
    )

    assert reference.sequence == sequence


@pytest.mark.parametrize(
    "invalid_sequence",
    [
        0,
        -1,
        -10,
    ],
)
def test_tie_match_reference_rejects_non_positive_sequence(
    invalid_sequence: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="maior ou igual a 1",
    ):
        TieMatchReference(
            match_id=MatchId.new(),
            sequence=invalid_sequence,
        )


@pytest.mark.parametrize(
    "invalid_sequence",
    [
        True,
        False,
        1.5,
        "1",
        None,
    ],
)
def test_tie_match_reference_rejects_invalid_sequence_type(
    invalid_sequence: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="sequence deve ser int",
    ):
        TieMatchReference(
            match_id=MatchId.new(),
            sequence=invalid_sequence,
        )


def test_tie_match_reference_rejects_invalid_match_id() -> None:
    with pytest.raises(
        TypeError,
        match="match_id deve ser MatchId",
    ):
        TieMatchReference(
            match_id="match-id",
            sequence=1,
        )


def test_tie_match_reference_uses_value_equality() -> None:
    match_id = MatchId.new()

    first = TieMatchReference(
        match_id=match_id,
        sequence=1,
    )

    second = TieMatchReference(
        match_id=match_id,
        sequence=1,
    )

    assert first == second
    assert hash(first) == hash(second)


def test_tie_match_reference_detects_different_sequence() -> None:
    match_id = MatchId.new()

    first = TieMatchReference(
        match_id=match_id,
        sequence=1,
    )

    second = TieMatchReference(
        match_id=match_id,
        sequence=2,
    )

    assert first != second


def test_tie_match_reference_is_immutable() -> None:
    reference = TieMatchReference(
        match_id=MatchId.new(),
        sequence=1,
    )

    with pytest.raises(FrozenInstanceError):
        reference.sequence = 2