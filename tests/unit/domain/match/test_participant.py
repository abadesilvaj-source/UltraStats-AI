"""Testes da entidade MatchParticipant."""

import pytest

from ultrastats_ai.domain.match import (
    MatchParticipant,
    MatchParticipantStatus,
)
from ultrastats_ai.domain.shared import (
    MatchId,
    MatchParticipantId,
    ParticipantRole,
    TeamId,
)


def valid_values() -> dict[str, object]:
    return {
        "id": MatchParticipantId.new(),
        "match_id": MatchId.new(),
        "team_id": TeamId.new(),
        "role": ParticipantRole.HOME,
        "order": 1,
        "status": MatchParticipantStatus.EXPECTED,
        "score": None,
        "is_winner": False,
        "is_tbd": False,
        "placeholder_name": None,
    }


def test_participant_is_created() -> None:
    values = valid_values()
    participant = MatchParticipant(**values)  # type: ignore[arg-type]

    assert participant.id == values["id"]
    assert participant.team_id == values["team_id"]


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        ("id", object(), "MatchParticipantId"),
        ("match_id", object(), "MatchId"),
        ("team_id", object(), "TeamId ou None"),
        ("role", "home", "ParticipantRole"),
        ("order", True, "order deve ser int"),
        ("order", 1.5, "order deve ser int"),
        ("status", "expected", "MatchParticipantStatus"),
        ("score", True, "score deve ser int ou None"),
        ("score", 1.5, "score deve ser int ou None"),
        ("is_winner", 1, "is_winner deve ser bool"),
        ("is_tbd", 1, "is_tbd deve ser bool"),
        ("placeholder_name", 1, "str ou None"),
    ],
)
def test_participant_rejects_invalid_types(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    values = valid_values()
    values[field_name] = invalid_value

    with pytest.raises(TypeError, match=message):
        MatchParticipant(**values)  # type: ignore[arg-type]


def test_participant_rejects_non_positive_order() -> None:
    values = valid_values()
    values["order"] = 0

    with pytest.raises(ValueError, match="maior que zero"):
        MatchParticipant(**values)  # type: ignore[arg-type]


def test_participant_rejects_negative_score() -> None:
    values = valid_values()
    values["score"] = -1

    with pytest.raises(ValueError, match="negativo"):
        MatchParticipant(**values)  # type: ignore[arg-type]


def test_tbd_participant_normalizes_placeholder() -> None:
    values = valid_values()
    values.update(
        team_id=None,
        is_tbd=True,
        placeholder_name="  Vencedor do confronto A  ",
    )

    participant = MatchParticipant(**values)  # type: ignore[arg-type]

    assert participant.placeholder_name == "Vencedor do confronto A"


def test_tbd_participant_rejects_team() -> None:
    values = valid_values()
    values.update(
        is_tbd=True,
        placeholder_name="A definir",
    )

    with pytest.raises(ValueError, match="não pode possuir team_id"):
        MatchParticipant(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("placeholder", [None, "", "   "])
def test_tbd_participant_requires_placeholder(
    placeholder: str | None,
) -> None:
    values = valid_values()
    values.update(
        team_id=None,
        is_tbd=True,
        placeholder_name=placeholder,
    )

    with pytest.raises(ValueError, match="placeholder_name"):
        MatchParticipant(**values)  # type: ignore[arg-type]


def test_defined_participant_requires_team() -> None:
    values = valid_values()
    values["team_id"] = None

    with pytest.raises(ValueError, match="exige team_id"):
        MatchParticipant(**values)  # type: ignore[arg-type]


def test_assign_team_resolves_placeholder() -> None:
    values = valid_values()
    values.update(
        team_id=None,
        is_tbd=True,
        placeholder_name="A definir",
    )
    participant = MatchParticipant(**values)  # type: ignore[arg-type]
    team_id = TeamId.new()

    resolved = participant.assign_team(team_id)

    assert resolved.team_id == team_id
    assert not resolved.is_tbd
    assert resolved.placeholder_name is None
    assert resolved.status is MatchParticipantStatus.CONFIRMED


def test_assign_team_rejects_invalid_id() -> None:
    values = valid_values()
    participant = MatchParticipant(**values)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="TeamId"):
        participant.assign_team("team")  # type: ignore[arg-type]


def test_record_score_returns_updated_participant() -> None:
    values = valid_values()
    participant = MatchParticipant(**values)  # type: ignore[arg-type]

    updated = participant.record_score(2, is_winner=True)

    assert updated.score == 2
    assert updated.is_winner
    assert participant.score is None


def test_change_status_returns_updated_participant() -> None:
    participant = MatchParticipant(  # type: ignore[arg-type]
        **valid_values()
    )

    updated = participant.change_status(
        MatchParticipantStatus.ACTIVE
    )

    assert updated.status is MatchParticipantStatus.ACTIVE


def test_change_status_rejects_invalid_type() -> None:
    participant = MatchParticipant(  # type: ignore[arg-type]
        **valid_values()
    )

    with pytest.raises(TypeError, match="MatchParticipantStatus"):
        participant.change_status("active")  # type: ignore[arg-type]
