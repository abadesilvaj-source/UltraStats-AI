"""Testes do Value Object CompetitionName."""

import pytest

from ultrastats_ai.domain.shared import (
    CompetitionName,
    ProperName,
)
from ultrastats_ai.domain.shared.names import (
    CompetitionName as NamesPackageCompetitionName,
)
from ultrastats_ai.domain.shared.names.competitions import (
    CompetitionName as CompetitionsPackageCompetitionName,
)


def test_competition_name_inherits_from_proper_name() -> None:
    competition = CompetitionName("Premier League")

    assert isinstance(competition, ProperName)


def test_competition_name_normalizes_whitespace() -> None:
    competition = CompetitionName("  UEFA    Champions   League  ")

    assert competition.value == "UEFA Champions League"


def test_competition_name_preserves_unicode_characters() -> None:
    competition = CompetitionName("Campeonato Brasileiro Série A")

    assert competition.value == "Campeonato Brasileiro Série A"


def test_competition_name_preserves_abbreviations() -> None:
    competition = CompetitionName("UEFA Champions League")

    assert competition.value == "UEFA Champions League"


def test_competition_name_equality_uses_value_and_type() -> None:
    first = CompetitionName("Copa do Brasil")
    second = CompetitionName("Copa do Brasil")

    assert first == second
    assert hash(first) == hash(second)


def test_competition_name_is_immutable() -> None:
    competition = CompetitionName("Premier League")

    with pytest.raises((AttributeError, TypeError)):
        competition.value = "La Liga"

def test_competition_name_is_distinct_from_other_name_types() -> None:
    from ultrastats_ai.domain.shared import VenueName

    competition = CompetitionName("Maracanã")
    venue = VenueName("Maracanã")

    assert competition != venue
    assert type(competition) is not type(venue)

def test_public_apis_export_same_competition_name_class() -> None:
    assert CompetitionName is NamesPackageCompetitionName
    assert CompetitionName is CompetitionsPackageCompetitionName