"""Factories compartilhadas pelos testes do Match Context."""

import pytest

from ultrastats_ai.domain.match import (
    Match,
    MatchParticipant,
    MatchParticipantStatus,
    MatchType,
)
from ultrastats_ai.domain.shared import (
    CompetitionId,
    DomainDate,
    MatchId,
    MatchParticipantId,
    MatchStatus,
    ParticipantRole,
    SeasonId,
    TeamId,
)


@pytest.fixture
def match_id() -> MatchId:
    return MatchId.new()


def make_participant(
    *,
    match_id: MatchId,
    role: ParticipantRole = ParticipantRole.HOME,
    order: int = 1,
    id: MatchParticipantId | None = None,
    team_id: TeamId | None = None,
    status: MatchParticipantStatus = MatchParticipantStatus.EXPECTED,
    score: int | None = None,
    is_winner: bool = False,
    is_tbd: bool = False,
    placeholder_name: str | None = None,
) -> MatchParticipant:
    return MatchParticipant(
        id=id or MatchParticipantId.new(),
        match_id=match_id,
        team_id=(
            None
            if is_tbd
            else team_id or TeamId.new()
        ),
        role=role,
        order=order,
        status=status,
        score=score,
        is_winner=is_winner,
        is_tbd=is_tbd,
        placeholder_name=placeholder_name,
    )


def make_match(
    *,
    id: MatchId | None = None,
    participants: tuple[
        MatchParticipant,
        MatchParticipant,
    ] | None = None,
    status: MatchStatus = MatchStatus.SCHEDULED,
) -> Match:
    current_id = id or MatchId.new()
    current_participants = participants or (
        make_participant(
            match_id=current_id,
            role=ParticipantRole.HOME,
            order=1,
        ),
        make_participant(
            match_id=current_id,
            role=ParticipantRole.AWAY,
            order=2,
        ),
    )

    return Match(
        id=current_id,
        competition_id=CompetitionId.new(),
        season_id=SeasonId.new(),
        match_type=MatchType.REGULAR,
        status=status,
        participants=current_participants,
        scheduled_date=(
            DomainDate("2026-08-01")
            if status is MatchStatus.SCHEDULED
            else None
        ),
    )
