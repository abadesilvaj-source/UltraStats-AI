"""Testes de OfficialRole."""

import pytest

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.enums.official_role import OfficialRole
from ultrastats_ai.domain.shared.errors import DomainValidationError


def test_official_role_inherits_from_domain_enum() -> None:
    assert issubclass(OfficialRole, DomainEnum)


def test_official_role_contains_expected_values() -> None:
    assert OfficialRole.values() == (
        "referee",
        "assistant_referee",
        "fourth_official",
        "video_assistant_referee",
        "assistant_video_assistant_referee",
        "additional_assistant_referee",
        "reserve_assistant_referee",
        "match_commissioner",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("referee", OfficialRole.REFEREE),
        ("REFEREE", OfficialRole.REFEREE),
        (
            "Assistant Referee",
            OfficialRole.ASSISTANT_REFEREE,
        ),
        (
            "fourth-official",
            OfficialRole.FOURTH_OFFICIAL,
        ),
        (
            "Video Assistant Referee",
            OfficialRole.VIDEO_ASSISTANT_REFEREE,
        ),
        (
            "assistant video assistant referee",
            OfficialRole.ASSISTANT_VIDEO_ASSISTANT_REFEREE,
        ),
        (
            "MATCH_COMMISSIONER",
            OfficialRole.MATCH_COMMISSIONER,
        ),
    ],
)
def test_official_role_parses_valid_values(
    value: str,
    expected: OfficialRole,
) -> None:
    assert OfficialRole.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "coach",
        "player",
        "unknown_official",
    ],
)
def test_official_role_rejects_invalid_values(value: str) -> None:
    with pytest.raises(DomainValidationError):
        OfficialRole.parse(value)


def test_official_role_has_value_recognizes_normalized_input() -> None:
    assert OfficialRole.has_value("Fourth Official")
    assert OfficialRole.has_value("VIDEO-ASSISTANT-REFEREE")
    assert not OfficialRole.has_value("unknown")


def test_official_role_is_serializable_as_string() -> None:
    assert str(OfficialRole.REFEREE) == "referee"