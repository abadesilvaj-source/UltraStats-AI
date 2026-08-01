"""Testes do Value Object PersonName."""

import pytest

from ultrastats_ai.domain.shared import PersonName, ProperName
from ultrastats_ai.domain.shared.names import (
    PersonName as NamesPackagePersonName,
)
from ultrastats_ai.domain.shared.names.people import (
    PersonName as PeoplePackagePersonName,
)


def test_person_name_inherits_from_proper_name() -> None:
    person_name = PersonName("Carlo Ancelotti")

    assert isinstance(person_name, ProperName)


def test_person_name_normalizes_whitespace() -> None:
    person_name = PersonName("  Carlo    Ancelotti  ")

    assert person_name.value == "Carlo Ancelotti"


def test_person_name_preserves_unicode_characters() -> None:
    person_name = PersonName("José Mourinho")

    assert person_name.value == "José Mourinho"


def test_person_name_accepts_single_word_name() -> None:
    person_name = PersonName("Pelé")

    assert person_name.value == "Pelé"


def test_person_name_preserves_hyphenated_names() -> None:
    person_name = PersonName("Jean-Pierre Papin")

    assert person_name.value == "Jean-Pierre Papin"


def test_person_name_preserves_apostrophes() -> None:
    person_name = PersonName("Shaquille O'Neal")

    assert person_name.value == "Shaquille O'Neal"


def test_person_name_equality_uses_value_and_type() -> None:
    first = PersonName("Xabi Alonso")
    second = PersonName("Xabi Alonso")

    assert first == second
    assert hash(first) == hash(second)


def test_person_name_is_immutable() -> None:
    person_name = PersonName("Carlo Ancelotti")

    with pytest.raises((AttributeError, TypeError)):
        person_name.value = "José Mourinho"


def test_person_name_is_distinct_from_other_name_types() -> None:
    from ultrastats_ai.domain.shared import CompetitionName

    person_name = PersonName("Premier League")
    competition_name = CompetitionName("Premier League")

    assert person_name != competition_name
    assert type(person_name) is not type(competition_name)


def test_public_apis_export_same_person_name_class() -> None:
    assert PersonName is NamesPackagePersonName
    assert PersonName is PeoplePackagePersonName