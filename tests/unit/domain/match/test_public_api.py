"""Testes da API pública do Match Context."""

import ultrastats_ai.domain.match as match_api


def test_match_public_api_is_explicit() -> None:
    assert set(match_api.__all__) == {
        "AppointmentStatus",
        "DecisionStatus",
        "DuplicateMatchParticipantError",
        "DuplicateMatchRecordError",
        "DuplicateMatchVenueError",
        "DuplicateScheduleChangeError",
        "EventStatus",
        "InterruptionStatus",
        "InvalidMatchParticipantsError",
        "InvalidMatchRecordError",
        "InvalidMatchScheduleError",
        "InvalidMatchStatusTransitionError",
        "InvalidMatchVenueError",
        "InvalidScheduleChangeError",
        "Lineup",
        "LineupEntry",
        "LineupRole",
        "LineupStatus",
        "LineupType",
        "Match",
        "MatchDecision",
        "MatchDomainError",
        "MatchEvent",
        "MatchInterruption",
        "MatchOfficial",
        "MatchParticipant",
        "MatchParticipantNotFoundError",
        "MatchParticipantOwnershipError",
        "MatchParticipantStatus",
        "MatchPeriod",
        "MatchRecordOwnershipError",
        "MatchRevision",
        "MatchScheduleChange",
        "MatchSquad",
        "MatchStatistic",
        "MatchType",
        "MatchVenue",
        "MatchVenueOwnershipError",
        "MultipleCurrentMatchVenuesError",
        "PeriodStatus",
        "PeriodType",
        "RevisionStatus",
        "ScheduleChangeOwnershipError",
        "SquadStatus",
        "SquadType",
        "StatisticScope",
        "StatisticUnit",
        "SurfaceCondition",
        "SurfaceType",
        "VenueRole",
        "VenueStatus",
        "WeatherCondition",
        "can_transition",
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
    assert (
        match_api.VenueStatus.parse("Pending Confirmation")
        is match_api.VenueStatus.PENDING_CONFIRMATION
    )
