"""Testes dos identificadores canônicos."""

from dataclasses import FrozenInstanceError
from uuid import UUID, uuid4

import pytest

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.identifiers import (
    CanonicalId,
    CompetitionId,
    CountryId,
    MatchId,
    MatchParticipantId,
    PlayerId,
    PredictionId,
    TeamId,
)


def test_canonical_id_accepts_uuid() -> None:
    uuid_value = uuid4()

    identifier = CanonicalId(value=uuid_value)

    assert identifier.value == uuid_value


def test_new_creates_uuid_identifier() -> None:
    identifier = TeamId.new()

    assert isinstance(identifier.value, UUID)


def test_new_creates_unique_identifiers() -> None:
    first = MatchId.new()
    second = MatchId.new()

    assert first != second
    assert first.value != second.value


def test_match_participant_identifier_is_canonical() -> None:
    identifier = MatchParticipantId.new()

    assert isinstance(identifier.value, UUID)


def test_from_string_creates_identifier() -> None:
    uuid_value = uuid4()

    identifier = CompetitionId.from_string(str(uuid_value))

    assert identifier.value == uuid_value


def test_from_string_removes_surrounding_spaces() -> None:
    uuid_value = uuid4()

    identifier = CountryId.from_string(f"  {uuid_value}  ")

    assert identifier.value == uuid_value


def test_string_representation_returns_uuid() -> None:
    uuid_value = uuid4()
    identifier = PlayerId(value=uuid_value)

    assert str(identifier) == str(uuid_value)


def test_same_identifier_type_and_value_are_equal() -> None:
    uuid_value = uuid4()

    first = TeamId(value=uuid_value)
    second = TeamId(value=uuid_value)

    assert first == second
    assert hash(first) == hash(second)


def test_different_identifier_types_are_not_equal() -> None:
    uuid_value = uuid4()

    team_id = TeamId(value=uuid_value)
    match_id = MatchId(value=uuid_value)

    assert team_id != match_id


def test_identifier_is_immutable() -> None:
    identifier = TeamId.new()

    with pytest.raises(FrozenInstanceError):
        identifier.value = uuid4()  # type: ignore[misc]


def test_identifier_can_be_used_as_dictionary_key() -> None:
    identifier = PredictionId.new()

    predictions = {
        identifier: "home-win",
    }

    assert predictions[identifier] == "home-win"


def test_identifier_rejects_non_uuid_value() -> None:
    with pytest.raises(
        DomainValidationError,
        match="deve ser um UUID",
    ):
        TeamId(value="invalid")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "invalid_value",
    [
        "",
        "   ",
        "not-a-uuid",
        "123",
        "00000000-0000-0000-0000",
    ],
)
def test_from_string_rejects_invalid_uuid(
    invalid_value: str,
) -> None:
    with pytest.raises(DomainValidationError):
        MatchId.from_string(invalid_value)


def test_from_string_rejects_non_string_value() -> None:
    with pytest.raises(
        DomainValidationError,
        match="deve ser uma string",
    ):
        MatchId.from_string(123)  # type: ignore[arg-type]
