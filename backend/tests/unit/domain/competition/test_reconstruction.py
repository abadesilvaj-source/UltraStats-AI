"""Testes dos estados de reconstrução do contexto Competition."""

from dataclasses import FrozenInstanceError

import pytest

from ultrastats_ai.domain.competition import (
    Competition,
    CompetitionAliases,
    CompetitionReconstruction,
    Round,
    RoundReconstruction,
    Season,
    SeasonReconstruction,
    Stage,
    StageReconstruction,
    Tie,
    TieMatchReference,
    TieReconstruction,
)
from ultrastats_ai.domain.shared import (
    AliasValue,
    CompetitionCode,
    CompetitionId,
    CompetitionName,
    CompetitionType,
    CountryId,
    DomainDate,
    MatchId,
    Name,
    PhaseType,
    RoundId,
    RoundNumber,
    RoundType,
    SeasonId,
    SeasonStatus,
    StageId,
    TieId,
)


# ============================================================
# CompetitionReconstruction
# ============================================================


def test_competition_reconstruction_preserves_complete_state(
) -> None:
    country_id = CountryId.new()

    aliases = CompetitionAliases(
        (
            AliasValue("Brasileirão"),
            AliasValue("Série A"),
        )
    )

    entity = Competition(
        id=CompetitionId.new(),
        code=CompetitionCode("BRA-A"),
        name=CompetitionName(
            "Campeonato Brasileiro Série A"
        ),
        competition_type=CompetitionType.LEAGUE,
        country_id=country_id,
        aliases=aliases,
        is_active=False,
    )

    state = CompetitionReconstruction.from_entity(
        entity
    )

    restored = state.restore()

    assert restored == entity
    assert restored is not entity
    assert restored.id == entity.id
    assert restored.code == entity.code
    assert restored.name == entity.name
    assert (
        restored.competition_type
        is entity.competition_type
    )
    assert restored.country_id == country_id
    assert restored.aliases == aliases
    assert restored.is_active is False


def test_competition_reconstruction_preserves_defaults(
    competition,
) -> None:
    state = CompetitionReconstruction.from_entity(
        competition
    )

    restored = state.restore()

    assert restored == competition
    assert restored.country_id is None
    assert restored.aliases == CompetitionAliases.empty()
    assert restored.is_active is True


def test_competition_reconstruction_rejects_invalid_entity(
) -> None:
    with pytest.raises(
        TypeError,
        match="entity deve ser Competition",
    ):
        CompetitionReconstruction.from_entity(
            object()
        )


# ============================================================
# SeasonReconstruction
# ============================================================


def test_season_reconstruction_preserves_complete_state(
    competition,
) -> None:
    aliases = CompetitionAliases(
        (
            AliasValue("Temporada atual"),
        )
    )

    entity = Season(
        id=SeasonId.new(),
        competition=competition,
        name=Name("2026"),
        status=SeasonStatus.ACTIVE,
        start_date=DomainDate("2026-01-01"),
        end_date=DomainDate("2026-12-31"),
        aliases=aliases,
        is_current=True,
        is_active=False,
    )

    state = SeasonReconstruction.from_entity(
        entity
    )

    restored = state.restore()

    assert restored == entity
    assert restored is not entity
    assert restored.id == entity.id
    assert restored.competition == competition
    assert restored.name == Name("2026")
    assert restored.status is SeasonStatus.ACTIVE
    assert restored.start_date == DomainDate(
        "2026-01-01"
    )
    assert restored.end_date == DomainDate(
        "2026-12-31"
    )
    assert restored.aliases == aliases
    assert restored.is_current is True
    assert restored.is_active is False


def test_season_reconstruction_preserves_defaults(
    season,
) -> None:
    state = SeasonReconstruction.from_entity(
        season
    )

    restored = state.restore()

    assert restored == season
    assert restored.start_date is None
    assert restored.end_date is None
    assert restored.aliases == CompetitionAliases.empty()
    assert restored.is_current is False
    assert restored.is_active is True


def test_season_reconstruction_rejects_invalid_entity(
) -> None:
    with pytest.raises(
        TypeError,
        match="entity deve ser Season",
    ):
        SeasonReconstruction.from_entity(
            object()
        )


# ============================================================
# StageReconstruction
# ============================================================


def test_stage_reconstruction_preserves_complete_state(
    season,
) -> None:
    aliases = CompetitionAliases(
        (
            AliasValue("Grupos"),
        )
    )

    entity = Stage(
        id=StageId.new(),
        season=season,
        name=Name("Fase de grupos"),
        phase_type=PhaseType.GROUP_STAGE,
        sequence=1,
        start_date=DomainDate("2026-01-01"),
        end_date=DomainDate("2026-03-31"),
        aliases=aliases,
        is_active=False,
    )

    state = StageReconstruction.from_entity(
        entity
    )

    restored = state.restore()

    assert restored == entity
    assert restored is not entity
    assert restored.id == entity.id
    assert restored.season == season
    assert restored.name == Name("Fase de grupos")
    assert restored.phase_type is PhaseType.GROUP_STAGE
    assert restored.sequence == 1
    assert restored.start_date == DomainDate(
        "2026-01-01"
    )
    assert restored.end_date == DomainDate(
        "2026-03-31"
    )
    assert restored.aliases == aliases
    assert restored.is_active is False


def test_stage_reconstruction_preserves_defaults(
    season,
) -> None:
    entity = Stage(
        id=StageId.new(),
        season=season,
        name=Name("Fase"),
        phase_type=PhaseType.GROUP_STAGE,
    )

    restored = (
        StageReconstruction
        .from_entity(entity)
        .restore()
    )

    assert restored == entity
    assert restored.sequence is None
    assert restored.start_date is None
    assert restored.end_date is None
    assert restored.aliases == CompetitionAliases.empty()
    assert restored.is_active is True


def test_stage_reconstruction_rejects_invalid_entity(
) -> None:
    with pytest.raises(
        TypeError,
        match="entity deve ser Stage",
    ):
        StageReconstruction.from_entity(
            object()
        )


# ============================================================
# RoundReconstruction
# ============================================================


def test_round_reconstruction_preserves_complete_state(
    season,
    stage,
) -> None:
    aliases = CompetitionAliases(
        (
            AliasValue("R1"),
        )
    )

    entity = Round(
        id=RoundId.new(),
        season=season,
        name=Name("Rodada 1"),
        round_type=RoundType.GROUP,
        stage=stage,
        round_number=RoundNumber(1),
        sequence=1,
        start_date=DomainDate("2026-01-01"),
        end_date=DomainDate("2026-01-02"),
        aliases=aliases,
        is_current=True,
        is_active=False,
    )

    state = RoundReconstruction.from_entity(
        entity
    )

    restored = state.restore()

    assert restored == entity
    assert restored is not entity
    assert restored.id == entity.id
    assert restored.season == season
    assert restored.stage == stage
    assert restored.name == Name("Rodada 1")
    assert restored.round_type is RoundType.GROUP
    assert restored.round_number == RoundNumber(1)
    assert restored.sequence == 1
    assert restored.start_date == DomainDate(
        "2026-01-01"
    )
    assert restored.end_date == DomainDate(
        "2026-01-02"
    )
    assert restored.aliases == aliases
    assert restored.is_current is True
    assert restored.is_active is False


def test_round_reconstruction_preserves_defaults(
    season,
) -> None:
    entity = Round(
        id=RoundId.new(),
        season=season,
        name=Name("Rodada"),
        round_type=RoundType.REGULAR,
    )

    restored = (
        RoundReconstruction
        .from_entity(entity)
        .restore()
    )

    assert restored == entity
    assert restored.stage is None
    assert restored.round_number is None
    assert restored.sequence is None
    assert restored.start_date is None
    assert restored.end_date is None
    assert restored.aliases == CompetitionAliases.empty()
    assert restored.is_current is False
    assert restored.is_active is True


def test_round_reconstruction_rejects_invalid_entity(
) -> None:
    with pytest.raises(
        TypeError,
        match="entity deve ser Round",
    ):
        RoundReconstruction.from_entity(
            object()
        )


# ============================================================
# TieReconstruction
# ============================================================


def test_tie_reconstruction_preserves_complete_state(
    competition,
    season,
    stage,
) -> None:
    first = TieMatchReference(
        match_id=MatchId.new(),
        sequence=1,
    )

    second = TieMatchReference(
        match_id=MatchId.new(),
        sequence=2,
    )

    entity = Tie(
        id=TieId.new(),
        competition=competition,
        season=season,
        stage=stage,
        matches=(first, second),
        is_active=False,
    )

    state = TieReconstruction.from_entity(
        entity
    )

    restored = state.restore()

    assert restored == entity
    assert restored is not entity
    assert restored.id == entity.id
    assert restored.competition == competition
    assert restored.season == season
    assert restored.stage == stage
    assert restored.matches == (first, second)
    assert restored.is_active is False


def test_tie_reconstruction_preserves_defaults(
    competition,
    season,
) -> None:
    entity = Tie(
        id=TieId.new(),
        competition=competition,
        season=season,
    )

    restored = (
        TieReconstruction
        .from_entity(entity)
        .restore()
    )

    assert restored == entity
    assert restored.stage is None
    assert restored.matches == ()
    assert restored.is_active is True


def test_tie_reconstruction_rejects_invalid_entity(
) -> None:
    with pytest.raises(
        TypeError,
        match="entity deve ser Tie",
    ):
        TieReconstruction.from_entity(
            object()
        )


# ============================================================
# Identidade e imutabilidade dos estados
# ============================================================


@pytest.mark.parametrize(
    "state_factory",
    [
        lambda competition, season, stage: (
            CompetitionReconstruction.from_entity(
                competition
            )
        ),
        lambda competition, season, stage: (
            SeasonReconstruction.from_entity(
                season
            )
        ),
        lambda competition, season, stage: (
            StageReconstruction.from_entity(
                stage
            )
        ),
    ],
)
def test_reconstruction_state_is_immutable(
    competition,
    season,
    stage,
    state_factory,
) -> None:
    state = state_factory(
        competition,
        season,
        stage,
    )

    with pytest.raises(FrozenInstanceError):
        state.id = CompetitionId.new()