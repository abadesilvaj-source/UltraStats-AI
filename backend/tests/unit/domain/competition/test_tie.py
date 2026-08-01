"""Testes do Aggregate Root conceitual Tie."""

from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from ultrastats_ai.domain.competition import (
    Competition,
    CompetitionHierarchyError,
    DuplicateTieMatchError,
    DuplicateTieMatchSequenceError,
    Season,
    Stage,
    Tie,
    TieMatchReference,
)
from ultrastats_ai.domain.shared import (
    CompetitionCode,
    CompetitionId,
    CompetitionName,
    CompetitionType,
    MatchId,
    Name,
    PhaseType,
    SeasonId,
    StageId,
    TieId,
)


_UNSET = object()


def make_tie(
    competition,
    season,
    *,
    id: Any = _UNSET,
    competition_value: Any = _UNSET,
    season_value: Any = _UNSET,
    stage: Any = _UNSET,
    matches: Any = _UNSET,
    is_active: Any = True,
) -> Tie:
    """Cria um confronto válido com campos sobrescrevíveis."""

    return Tie(
        id=(
            TieId.new()
            if id is _UNSET
            else id
        ),
        competition=(
            competition
            if competition_value is _UNSET
            else competition_value
        ),
        season=(
            season
            if season_value is _UNSET
            else season_value
        ),
        stage=(
            None
            if stage is _UNSET
            else stage
        ),
        matches=(
            ()
            if matches is _UNSET
            else matches
        ),
        is_active=is_active,
    )


def make_other_competition() -> Competition:
    """Cria uma competição diferente da fixture principal."""

    return Competition(
        id=CompetitionId.new(),
        code=CompetitionCode("OTHER"),
        name=CompetitionName("Outra competição"),
        competition_type=CompetitionType.CUP,
    )


def make_season_for_competition(
    competition: Competition,
) -> Season:
    """Cria uma temporada para uma competição específica."""

    return Season(
        id=SeasonId.new(),
        competition=competition,
        name=Name("2026"),
    )


def make_stage_for_season(
    season: Season,
) -> Stage:
    """Cria uma fase para uma temporada específica."""

    return Stage(
        id=StageId.new(),
        season=season,
        name=Name("Fase"),
        phase_type=PhaseType.GROUP_STAGE,
    )


def make_match_reference(
    *,
    match_id: MatchId | None = None,
    sequence: int = 1,
) -> TieMatchReference:
    """Cria uma referência válida de partida."""

    return TieMatchReference(
        match_id=(
            MatchId.new()
            if match_id is None
            else match_id
        ),
        sequence=sequence,
    )


# ============================================================
# Criação
# ============================================================


def test_tie_is_created_with_required_fields(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
    )

    assert isinstance(tie.id, TieId)
    assert tie.competition == competition
    assert tie.season == season
    assert tie.stage is None
    assert tie.matches == ()
    assert tie.ordered_matches == ()
    assert tie.is_active is True


def test_tie_accepts_optional_fields(
    competition,
    season,
    stage,
) -> None:
    first = make_match_reference(sequence=1)
    second = make_match_reference(sequence=2)

    tie = make_tie(
        competition,
        season,
        stage=stage,
        matches=(first, second),
        is_active=False,
    )

    assert tie.stage == stage
    assert tie.matches == (first, second)
    assert tie.is_active is False


# ============================================================
# Validações básicas
# ============================================================


def test_tie_rejects_invalid_id_type(
    competition,
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="id deve ser TieId",
    ):
        make_tie(
            competition,
            season,
            id="invalid",
        )


def test_tie_rejects_invalid_competition_type(
    competition,
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "competition deve ser Competition"
        ),
    ):
        make_tie(
            competition,
            season,
            competition_value="invalid",
        )


def test_tie_rejects_invalid_season_type(
    competition,
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="season deve ser Season",
    ):
        make_tie(
            competition,
            season,
            season_value="invalid",
        )


def test_tie_rejects_invalid_stage_type(
    competition,
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match="stage deve ser Stage ou None",
    ):
        make_tie(
            competition,
            season,
            stage="invalid",
        )


def test_tie_rejects_non_tuple_matches(
    competition,
    season,
) -> None:
    reference = make_match_reference()

    with pytest.raises(
        TypeError,
        match="matches deve ser tuple",
    ):
        make_tie(
            competition,
            season,
            matches=[reference],
        )


@pytest.mark.parametrize(
    "invalid_is_active",
    [
        1,
        0,
        "true",
        None,
    ],
)
def test_tie_rejects_invalid_is_active_type(
    competition,
    season,
    invalid_is_active: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="is_active deve ser bool",
    ):
        make_tie(
            competition,
            season,
            is_active=invalid_is_active,
        )


def test_tie_rejects_invalid_match_item(
    competition,
    season,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "matches deve conter somente "
            "TieMatchReference"
        ),
    ):
        make_tie(
            competition,
            season,
            matches=("invalid",),
        )


# ============================================================
# Hierarquia
# ============================================================


def test_tie_accepts_season_from_competition(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
    )

    assert tie.season.competition.id == competition.id


def test_tie_rejects_season_from_another_competition(
    competition,
) -> None:
    other_competition = make_other_competition()
    other_season = make_season_for_competition(
        other_competition
    )

    with pytest.raises(
        CompetitionHierarchyError,
        match=(
            "A temporada do confronto deve pertencer "
            "à competição informada"
        ),
    ):
        make_tie(
            competition,
            other_season,
        )


def test_tie_accepts_stage_from_same_season(
    competition,
    season,
    stage,
) -> None:
    tie = make_tie(
        competition,
        season,
        stage=stage,
    )

    assert tie.stage == stage
    assert tie.stage.season.id == season.id


def test_tie_rejects_stage_from_another_season(
    competition,
    season,
) -> None:
    other_season = Season(
        id=SeasonId.new(),
        competition=competition,
        name=Name("2027"),
    )

    other_stage = make_stage_for_season(
        other_season
    )

    with pytest.raises(
        CompetitionHierarchyError,
        match=(
            "A fase do confronto deve pertencer "
            "à temporada informada"
        ),
    ):
        make_tie(
            competition,
            season,
            stage=other_stage,
        )


# ============================================================
# Ordenação das partidas
# ============================================================


def test_tie_orders_matches_by_sequence(
    competition,
    season,
) -> None:
    first = make_match_reference(sequence=1)
    second = make_match_reference(sequence=2)
    third = make_match_reference(sequence=3)

    tie = make_tie(
        competition,
        season,
        matches=(third, first, second),
    )

    assert tie.ordered_matches == (
        first,
        second,
        third,
    )


def test_ordered_matches_does_not_mutate_original_tuple(
    competition,
    season,
) -> None:
    first = make_match_reference(sequence=1)
    second = make_match_reference(sequence=2)

    tie = make_tie(
        competition,
        season,
        matches=(second, first),
    )

    ordered = tie.ordered_matches

    assert ordered == (first, second)
    assert tie.matches == (second, first)


# ============================================================
# Duplicidades
# ============================================================


def test_tie_rejects_duplicate_match(
    competition,
    season,
) -> None:
    match_id = MatchId.new()

    first = make_match_reference(
        match_id=match_id,
        sequence=1,
    )

    second = make_match_reference(
        match_id=match_id,
        sequence=2,
    )

    with pytest.raises(
        DuplicateTieMatchError,
        match=(
            "Uma partida não pode aparecer mais "
            "de uma vez no confronto"
        ),
    ):
        make_tie(
            competition,
            season,
            matches=(first, second),
        )


def test_tie_rejects_duplicate_sequence(
    competition,
    season,
) -> None:
    first = make_match_reference(sequence=1)
    second = make_match_reference(sequence=1)

    with pytest.raises(
        DuplicateTieMatchSequenceError,
        match=(
            "A sequência das partidas deve ser única"
        ),
    ):
        make_tie(
            competition,
            season,
            matches=(first, second),
        )


def test_tie_checks_duplicate_match_before_sequence(
    competition,
    season,
) -> None:
    match_id = MatchId.new()

    first = make_match_reference(
        match_id=match_id,
        sequence=1,
    )

    second = make_match_reference(
        match_id=match_id,
        sequence=1,
    )

    with pytest.raises(DuplicateTieMatchError):
        make_tie(
            competition,
            season,
            matches=(first, second),
        )


# ============================================================
# Adição de partida
# ============================================================


def test_tie_adds_match_immutably(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
    )

    reference = make_match_reference()

    updated = tie.add_match(reference)

    assert updated is not tie
    assert updated == tie
    assert updated.matches == (reference,)
    assert tie.matches == ()


def test_tie_add_match_preserves_existing_matches(
    competition,
    season,
) -> None:
    first = make_match_reference(sequence=1)
    second = make_match_reference(sequence=2)

    tie = make_tie(
        competition,
        season,
        matches=(first,),
    )

    updated = tie.add_match(second)

    assert updated.matches == (
        first,
        second,
    )
    assert tie.matches == (first,)


def test_tie_add_match_rejects_invalid_type(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
    )

    with pytest.raises(
        TypeError,
        match=(
            "reference deve ser TieMatchReference"
        ),
    ):
        tie.add_match("invalid")


def test_tie_add_match_reuses_duplicate_match_validation(
    competition,
    season,
) -> None:
    reference = make_match_reference()

    tie = make_tie(
        competition,
        season,
        matches=(reference,),
    )

    duplicate = make_match_reference(
        match_id=reference.match_id,
        sequence=2,
    )

    with pytest.raises(DuplicateTieMatchError):
        tie.add_match(duplicate)


def test_tie_add_match_reuses_duplicate_sequence_validation(
    competition,
    season,
) -> None:
    first = make_match_reference(sequence=1)

    tie = make_tie(
        competition,
        season,
        matches=(first,),
    )

    second = make_match_reference(sequence=1)

    with pytest.raises(
        DuplicateTieMatchSequenceError
    ):
        tie.add_match(second)


# ============================================================
# Remoção de partida
# ============================================================


def test_tie_removes_match_immutably(
    competition,
    season,
) -> None:
    first = make_match_reference(sequence=1)
    second = make_match_reference(sequence=2)

    tie = make_tie(
        competition,
        season,
        matches=(first, second),
    )

    updated = tie.remove_match(
        first.match_id
    )

    assert updated is not tie
    assert updated == tie
    assert updated.matches == (second,)
    assert tie.matches == (first, second)


def test_tie_remove_match_rejects_invalid_id_type(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
    )

    with pytest.raises(
        TypeError,
        match="match_id deve ser MatchId",
    ):
        tie.remove_match("invalid")


def test_tie_remove_match_rejects_unknown_match(
    competition,
    season,
) -> None:
    reference = make_match_reference()

    tie = make_tie(
        competition,
        season,
        matches=(reference,),
    )

    with pytest.raises(
        ValueError,
        match=(
            "A partida não pertence ao confronto"
        ),
    ):
        tie.remove_match(MatchId.new())


def test_tie_can_remove_only_match(
    competition,
    season,
) -> None:
    reference = make_match_reference()

    tie = make_tie(
        competition,
        season,
        matches=(reference,),
    )

    updated = tie.remove_match(
        reference.match_id
    )

    assert updated.matches == ()
    assert tie.matches == (reference,)


# ============================================================
# Estado de atividade
# ============================================================


def test_tie_can_be_deactivated(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
    )

    updated = tie.deactivate()

    assert updated is not tie
    assert updated == tie
    assert updated.is_active is False
    assert tie.is_active is True


def test_tie_can_be_activated(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
        is_active=False,
    )

    updated = tie.activate()

    assert updated is not tie
    assert updated == tie
    assert updated.is_active is True
    assert tie.is_active is False


def test_tie_activate_preserves_active_state(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
        is_active=True,
    )

    updated = tie.activate()

    assert updated is not tie
    assert updated.is_active is True


def test_tie_deactivate_preserves_inactive_state(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
        is_active=False,
    )

    updated = tie.deactivate()

    assert updated is not tie
    assert updated.is_active is False


# ============================================================
# Identidade
# ============================================================


def test_tie_is_compared_by_identity(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
    )

    updated = tie.deactivate()

    assert updated == tie
    assert hash(updated) == hash(tie)


def test_ties_with_different_ids_are_not_equal(
    competition,
    season,
) -> None:
    first = make_tie(
        competition,
        season,
    )

    second = make_tie(
        competition,
        season,
    )

    assert first != second


def test_tie_equality_returns_not_equal_for_other_type(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
    )

    assert tie != object()


def test_tie_hash_is_based_on_id(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
    )

    assert hash(tie) == hash(tie.id)


# ============================================================
# Imutabilidade
# ============================================================


def test_tie_is_immutable(
    competition,
    season,
) -> None:
    tie = make_tie(
        competition,
        season,
    )

    with pytest.raises(FrozenInstanceError):
        tie.is_active = False