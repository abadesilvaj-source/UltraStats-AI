"""Testes dos contratos de repository de Competition."""

from inspect import signature

from ultrastats_ai.domain.competition import (
    CompetitionHistoryRepository,
    CompetitionRepository,
    SeasonRepository,
    TieRepository,
)


def test_competition_repository_exposes_expected_methods() -> None:
    assert hasattr(CompetitionRepository, "get_by_id")
    assert hasattr(CompetitionRepository, "save")
    assert hasattr(CompetitionRepository, "delete")
    assert hasattr(CompetitionRepository, "list_all")


def test_competition_repository_get_by_id_signature() -> None:
    parameters = signature(
        CompetitionRepository.get_by_id
    ).parameters

    assert tuple(parameters) == (
        "self",
        "competition_id",
    )


def test_competition_repository_save_signature() -> None:
    parameters = signature(
        CompetitionRepository.save
    ).parameters

    assert tuple(parameters) == (
        "self",
        "competition",
    )


def test_competition_repository_delete_signature() -> None:
    parameters = signature(
        CompetitionRepository.delete
    ).parameters

    assert tuple(parameters) == (
        "self",
        "competition_id",
    )


def test_competition_repository_list_all_signature() -> None:
    parameters = signature(
        CompetitionRepository.list_all
    ).parameters

    assert tuple(parameters) == ("self",)


def test_season_repository_exposes_expected_methods() -> None:
    assert hasattr(SeasonRepository, "get_by_id")
    assert hasattr(
        SeasonRepository,
        "list_by_competition",
    )
    assert hasattr(SeasonRepository, "save")
    assert hasattr(SeasonRepository, "delete")


def test_season_repository_get_by_id_signature() -> None:
    parameters = signature(
        SeasonRepository.get_by_id
    ).parameters

    assert tuple(parameters) == (
        "self",
        "season_id",
    )


def test_season_repository_list_signature() -> None:
    parameters = signature(
        SeasonRepository.list_by_competition
    ).parameters

    assert tuple(parameters) == (
        "self",
        "competition_id",
    )


def test_season_repository_save_signature() -> None:
    parameters = signature(
        SeasonRepository.save
    ).parameters

    assert tuple(parameters) == (
        "self",
        "season",
    )


def test_season_repository_delete_signature() -> None:
    parameters = signature(
        SeasonRepository.delete
    ).parameters

    assert tuple(parameters) == (
        "self",
        "season_id",
    )


def test_tie_repository_exposes_expected_methods() -> None:
    assert hasattr(TieRepository, "get_by_id")
    assert hasattr(TieRepository, "list_by_season")
    assert hasattr(TieRepository, "save")
    assert hasattr(TieRepository, "delete")


def test_tie_repository_get_by_id_signature() -> None:
    parameters = signature(
        TieRepository.get_by_id
    ).parameters

    assert tuple(parameters) == (
        "self",
        "tie_id",
    )


def test_tie_repository_list_by_season_signature() -> None:
    parameters = signature(
        TieRepository.list_by_season
    ).parameters

    assert tuple(parameters) == (
        "self",
        "season_id",
    )


def test_tie_repository_save_signature() -> None:
    parameters = signature(
        TieRepository.save
    ).parameters

    assert tuple(parameters) == (
        "self",
        "tie",
    )


def test_tie_repository_delete_signature() -> None:
    parameters = signature(
        TieRepository.delete
    ).parameters

    assert tuple(parameters) == (
        "self",
        "tie_id",
    )


def test_history_repository_exposes_expected_methods() -> None:
    assert hasattr(
        CompetitionHistoryRepository,
        "append",
    )
    assert hasattr(
        CompetitionHistoryRepository,
        "get_by_id",
    )
    assert hasattr(
        CompetitionHistoryRepository,
        "list_for_entity",
    )


def test_history_repository_append_signature() -> None:
    parameters = signature(
        CompetitionHistoryRepository.append
    ).parameters

    assert tuple(parameters) == (
        "self",
        "entry",
    )


def test_history_repository_get_by_id_signature() -> None:
    parameters = signature(
        CompetitionHistoryRepository.get_by_id
    ).parameters

    assert tuple(parameters) == (
        "self",
        "history_id",
    )


def test_history_repository_list_for_entity_signature() -> None:
    parameters = signature(
        CompetitionHistoryRepository.list_for_entity
    ).parameters

    assert tuple(parameters) == (
        "self",
        "entity_id",
    )