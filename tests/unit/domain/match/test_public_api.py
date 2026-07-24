"""Testes da API pública do Match Context."""

import ultrastats_ai.domain.match as match_api


def test_match_public_api_is_explicit() -> None:
    assert set(match_api.__all__) == {
        "DuplicateMatchParticipantError",
        "InvalidMatchParticipantsError",
        "InvalidMatchScheduleError",
        "Match",
        "MatchDomainError",
        "MatchParticipant",
        "MatchParticipantNotFoundError",
        "MatchParticipantOwnershipError",
        "MatchParticipantStatus",
        "MatchType",
    }


def test_match_enums_parse_normalized_values() -> None:
    assert (
        match_api.MatchType.parse("Group Stage")
        is match_api.MatchType.GROUP_STAGE
    )
    assert (
        match_api.MatchParticipantStatus.parse("confirmed")
        is match_api.MatchParticipantStatus.CONFIRMED
    )
