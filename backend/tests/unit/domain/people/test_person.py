"""Testes do Aggregate Root Person."""

from dataclasses import FrozenInstanceError

import pytest

from ultrastats_ai.domain.people import (
    Coach,
    CoachRole,
    CoachStatus,
    Person,
    PersonAlreadyActiveError,
    PersonAlreadyInactiveError,
    PersonNameAliasConflictError,
    PersonProfileAlreadyExistsError,
    PersonProfileNotFoundError,
    PersonProfileOwnershipError,
    Player,
    PlayerStatus,
    Referee,
    RefereeRole,
    RefereeStatus,
)
from ultrastats_ai.domain.shared import (
    AliasValue,
    CoachId,
    DisplayName,
    DomainDate,
    PersonId,
    PersonName,
    PlayerId,
    RefereeId,
)


def make_person(
    *,
    id: PersonId | object | None = None,
    name: PersonName | object | None = None,
    display_name: DisplayName | object | None = None,
    birth_date: DomainDate | object | None = None,
    is_active: bool | object = True,
) -> Person:
    return Person(
        id=PersonId.new() if id is None else id,
        name=(
            PersonName("Neymar da Silva Santos Júnior")
            if name is None
            else name
        ),
        display_name=display_name,
        birth_date=birth_date,
        is_active=is_active,
    )


def make_player(person_id: PersonId) -> Player:
    return Player(
        id=PlayerId.new(),
        person_id=person_id,
        status=PlayerStatus.PROFESSIONAL,
    )


def make_coach(person_id: PersonId) -> Coach:
    return Coach(
        id=CoachId.new(),
        person_id=person_id,
        role=CoachRole.HEAD_COACH,
        status=CoachStatus.ACTIVE,
    )


def make_referee(person_id: PersonId) -> Referee:
    return Referee(
        id=RefereeId.new(),
        person_id=person_id,
        primary_role=RefereeRole.MAIN_REFEREE,
        status=RefereeStatus.ACTIVE,
    )


def test_person_is_created() -> None:
    person = make_person()

    assert isinstance(person.id, PersonId)
    assert isinstance(person.name, PersonName)
    assert person.player is None
    assert person.coach is None
    assert person.referee is None
    assert person.is_active is True


def test_person_rejects_invalid_id() -> None:
    with pytest.raises(
        TypeError,
        match="id deve ser PersonId",
    ):
        make_person(id="invalid")


def test_person_rejects_invalid_name() -> None:
    with pytest.raises(
        TypeError,
        match="name deve ser PersonName",
    ):
        make_person(name="Neymar")


def test_person_changes_name_immutably() -> None:
    person = make_person()
    new_name = PersonName("Neymar Júnior")

    updated = person.rename(new_name)

    assert updated is not person
    assert updated == person
    assert updated.name == new_name
    assert updated.id == person.id


def test_person_adds_alias_immutably() -> None:
    person = make_person()
    alias = AliasValue("Neymar")

    updated = person.add_alias(alias)

    assert updated is not person
    assert alias in updated.aliases
    assert alias not in person.aliases


def test_person_rejects_name_as_alias() -> None:
    person = make_person()

    with pytest.raises(
        PersonNameAliasConflictError
    ):
        person.add_alias(
            AliasValue(
                "NEYMAR DA SILVA SANTOS JÚNIOR"
            )
        )


def test_person_rejects_rename_to_existing_alias() -> None:
    person = make_person().add_alias(
        AliasValue("Neymar")
    )

    with pytest.raises(
        PersonNameAliasConflictError
    ):
        person.rename(
            PersonName("NEYMAR")
        )


def test_person_removes_alias() -> None:
    alias = AliasValue("Neymar")
    person = make_person().add_alias(alias)

    updated = person.remove_alias(alias)

    assert alias not in updated.aliases
    assert alias in person.aliases


def test_person_adds_player() -> None:
    person = make_person()
    player = make_player(person.id)

    updated = person.add_player(player)

    assert updated.player == player
    assert person.player is None


def test_person_rejects_player_from_another_person() -> None:
    person = make_person()
    player = make_player(PersonId.new())

    with pytest.raises(
        PersonProfileOwnershipError
    ):
        person.add_player(player)


def test_person_rejects_duplicate_player_profile() -> None:
    person = make_person()
    first = make_player(person.id)
    second = make_player(person.id)

    person = person.add_player(first)

    with pytest.raises(
        PersonProfileAlreadyExistsError
    ):
        person.add_player(second)


def test_person_removes_player() -> None:
    person = make_person()
    player = make_player(person.id)

    person = person.add_player(player)
    updated = person.remove_player()

    assert updated.player is None
    assert person.player == player


def test_person_rejects_removing_missing_player() -> None:
    person = make_person()

    with pytest.raises(
        PersonProfileNotFoundError
    ):
        person.remove_player()


def test_person_adds_and_removes_coach() -> None:
    person = make_person()
    coach = make_coach(person.id)

    with_coach = person.add_coach(coach)
    without_coach = with_coach.remove_coach()

    assert with_coach.coach == coach
    assert without_coach.coach is None


def test_person_rejects_duplicate_coach() -> None:
    person = make_person()
    first = make_coach(person.id)
    second = make_coach(person.id)

    person = person.add_coach(first)

    with pytest.raises(
        PersonProfileAlreadyExistsError
    ):
        person.add_coach(second)


def test_person_rejects_removing_missing_coach() -> None:
    with pytest.raises(
        PersonProfileNotFoundError
    ):
        make_person().remove_coach()


def test_person_adds_and_removes_referee() -> None:
    person = make_person()
    referee = make_referee(person.id)

    with_referee = person.add_referee(referee)
    without_referee = with_referee.remove_referee()

    assert with_referee.referee == referee
    assert without_referee.referee is None


def test_person_rejects_duplicate_referee() -> None:
    person = make_person()
    first = make_referee(person.id)
    second = make_referee(person.id)

    person = person.add_referee(first)

    with pytest.raises(
        PersonProfileAlreadyExistsError
    ):
        person.add_referee(second)


def test_person_rejects_removing_missing_referee() -> None:
    with pytest.raises(
        PersonProfileNotFoundError
    ):
        make_person().remove_referee()


def test_person_can_have_multiple_profile_types() -> None:
    person = make_person()

    updated = (
        person
        .add_player(make_player(person.id))
        .add_coach(make_coach(person.id))
        .add_referee(make_referee(person.id))
    )

    assert updated.player is not None
    assert updated.coach is not None
    assert updated.referee is not None


def test_person_deactivates_and_activates() -> None:
    person = make_person()

    inactive = person.deactivate()
    active = inactive.activate()

    assert inactive.is_active is False
    assert active.is_active is True


def test_person_rejects_duplicate_deactivation() -> None:
    person = make_person().deactivate()

    with pytest.raises(
        PersonAlreadyInactiveError
    ):
        person.deactivate()


def test_person_rejects_duplicate_activation() -> None:
    person = make_person()

    with pytest.raises(
        PersonAlreadyActiveError
    ):
        person.activate()


def test_person_equality_is_based_on_id() -> None:
    person = make_person()
    updated = person.add_alias(
        AliasValue("Neymar")
    )

    assert updated == person
    assert hash(updated) == hash(person)


def test_people_with_different_ids_are_not_equal() -> None:
    first = make_person()
    second = make_person()

    assert first != second


def test_person_is_not_equal_to_other_type() -> None:
    assert make_person() != object()


def test_person_is_immutable() -> None:
    person = make_person()

    with pytest.raises(FrozenInstanceError):
        person.is_active = False