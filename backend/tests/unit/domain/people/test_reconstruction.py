"""Testes da reconstrução controlada do People Context."""

import pytest

from ultrastats_ai.domain.people import (
    Coach,
    CoachRole,
    CoachStatus,
    InvalidProfessionalPeriodError,
    Person,
    PersonAliases,
    PersonProfileOwnershipError,
    Player,
    PlayerStatus,
    Referee,
    RefereeCategory,
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
    ShortName,
)


def test_player_reconstructs_persisted_state() -> None:
    player_id = PlayerId.new()
    person_id = PersonId.new()
    debut_date = DomainDate("2015-01-01")
    shirt_name = ShortName("Neymar")

    player = Player.reconstruct(
        id=player_id,
        person_id=person_id,
        status=PlayerStatus.PROFESSIONAL,
        professional_debut_date=debut_date,
        shirt_name=shirt_name,
        is_retired=False,
        is_active=True,
    )

    assert player.id == player_id
    assert player.person_id == person_id
    assert player.status is PlayerStatus.PROFESSIONAL
    assert player.professional_debut_date == debut_date
    assert player.shirt_name == shirt_name
    assert player.is_active is True


def test_player_reconstruction_preserves_retirement() -> None:
    player = Player.reconstruct(
        id=PlayerId.new(),
        person_id=PersonId.new(),
        status=PlayerStatus.RETIRED,
        retirement_date=DomainDate("2040-01-01"),
        is_retired=True,
        is_active=False,
    )

    assert player.status is PlayerStatus.RETIRED
    assert player.is_retired is True
    assert player.is_active is False


def test_player_reconstruction_validates_period() -> None:
    with pytest.raises(
        InvalidProfessionalPeriodError
    ):
        Player.reconstruct(
            id=PlayerId.new(),
            person_id=PersonId.new(),
            status=PlayerStatus.RETIRED,
            professional_debut_date=DomainDate(
                "2020-01-01"
            ),
            retirement_date=DomainDate(
                "2019-01-01"
            ),
            is_retired=True,
        )


def test_coach_reconstructs_persisted_state() -> None:
    coach_id = CoachId.new()
    person_id = PersonId.new()

    coach = Coach.reconstruct(
        id=coach_id,
        person_id=person_id,
        role=CoachRole.HEAD_COACH,
        status=CoachStatus.ACTIVE,
        coaching_license="UEFA PRO",
        professional_debut_date=DomainDate(
            "2010-01-01"
        ),
        is_active=True,
    )

    assert coach.id == coach_id
    assert coach.person_id == person_id
    assert coach.role is CoachRole.HEAD_COACH
    assert coach.status is CoachStatus.ACTIVE
    assert coach.coaching_license == "UEFA PRO"


def test_coach_reconstruction_preserves_retirement() -> None:
    coach = Coach.reconstruct(
        id=CoachId.new(),
        person_id=PersonId.new(),
        role=CoachRole.HEAD_COACH,
        status=CoachStatus.RETIRED,
        retirement_date=DomainDate("2040-01-01"),
        is_retired=True,
        is_active=False,
    )

    assert coach.status is CoachStatus.RETIRED
    assert coach.is_retired is True
    assert coach.is_active is False


def test_referee_reconstructs_persisted_state() -> None:
    referee_id = RefereeId.new()
    person_id = PersonId.new()

    referee = Referee.reconstruct(
        id=referee_id,
        person_id=person_id,
        primary_role=RefereeRole.MAIN_REFEREE,
        status=RefereeStatus.ACTIVE,
        category=RefereeCategory.INTERNATIONAL,
        federation_name="CBF",
        international_badge="FIFA",
        professional_debut_date=DomainDate(
            "2014-01-01"
        ),
        international_debut_date=DomainDate(
            "2018-01-01"
        ),
        is_international=True,
        is_active=True,
    )

    assert referee.id == referee_id
    assert referee.person_id == person_id
    assert referee.primary_role is RefereeRole.MAIN_REFEREE
    assert referee.status is RefereeStatus.ACTIVE
    assert (
        referee.category
        is RefereeCategory.INTERNATIONAL
    )
    assert referee.federation_name == "CBF"
    assert referee.international_badge == "FIFA"
    assert referee.is_international is True


def test_referee_reconstruction_preserves_retirement() -> None:
    referee = Referee.reconstruct(
        id=RefereeId.new(),
        person_id=PersonId.new(),
        primary_role=RefereeRole.MAIN_REFEREE,
        status=RefereeStatus.RETIRED,
        retirement_date=DomainDate("2040-01-01"),
        is_retired=True,
        is_active=False,
    )

    assert referee.status is RefereeStatus.RETIRED
    assert referee.is_retired is True
    assert referee.is_active is False


def test_person_reconstructs_without_profiles() -> None:
    person_id = PersonId.new()
    name = PersonName("Neymar da Silva Santos Júnior")
    display_name = DisplayName("Neymar")
    birth_date = DomainDate("1992-02-05")
    aliases = PersonAliases(
        (
            AliasValue("Neymar Jr."),
        )
    )

    person = Person.reconstruct(
        id=person_id,
        name=name,
        display_name=display_name,
        birth_date=birth_date,
        aliases=aliases,
        is_active=True,
    )

    assert person.id == person_id
    assert person.name == name
    assert person.display_name == display_name
    assert person.birth_date == birth_date
    assert person.aliases == aliases
    assert person.player is None
    assert person.coach is None
    assert person.referee is None
    assert person.is_active is True


def test_person_reconstructs_with_empty_aliases_by_default() -> None:
    person = Person.reconstruct(
        id=PersonId.new(),
        name=PersonName("Nome da Pessoa"),
    )

    assert person.aliases == PersonAliases.empty()


def test_person_reconstructs_complete_aggregate() -> None:
    person_id = PersonId.new()

    player = Player.reconstruct(
        id=PlayerId.new(),
        person_id=person_id,
        status=PlayerStatus.PROFESSIONAL,
    )

    coach = Coach.reconstruct(
        id=CoachId.new(),
        person_id=person_id,
        role=CoachRole.ASSISTANT_COACH,
        status=CoachStatus.ACTIVE,
    )

    referee = Referee.reconstruct(
        id=RefereeId.new(),
        person_id=person_id,
        primary_role=RefereeRole.VIDEO_ASSISTANT_REFEREE,
        status=RefereeStatus.ACTIVE,
    )

    person = Person.reconstruct(
        id=person_id,
        name=PersonName("Nome da Pessoa"),
        aliases=PersonAliases(
            (
                AliasValue("Nome Alternativo"),
            )
        ),
        player=player,
        coach=coach,
        referee=referee,
        is_active=False,
    )

    assert person.player == player
    assert person.coach == coach
    assert person.referee == referee
    assert person.is_active is False


@pytest.mark.parametrize(
    "profile_name",
    [
        "player",
        "coach",
        "referee",
    ],
)
def test_person_reconstruction_rejects_foreign_profile(
    profile_name: str,
) -> None:
    person_id = PersonId.new()
    foreign_person_id = PersonId.new()

    profiles: dict[str, object] = {
        "player": Player.reconstruct(
            id=PlayerId.new(),
            person_id=foreign_person_id,
            status=PlayerStatus.PROFESSIONAL,
        ),
        "coach": Coach.reconstruct(
            id=CoachId.new(),
            person_id=foreign_person_id,
            role=CoachRole.HEAD_COACH,
            status=CoachStatus.ACTIVE,
        ),
        "referee": Referee.reconstruct(
            id=RefereeId.new(),
            person_id=foreign_person_id,
            primary_role=RefereeRole.MAIN_REFEREE,
            status=RefereeStatus.ACTIVE,
        ),
    }

    profile_arguments = {
        profile_name: profiles[profile_name],
    }

    with pytest.raises(
        PersonProfileOwnershipError
    ):
        Person.reconstruct(
            id=person_id,
            name=PersonName("Nome da Pessoa"),
            **profile_arguments,
        )


def test_person_reconstruction_rejects_invalid_alias_type() -> None:
    with pytest.raises(
        TypeError,
        match="aliases deve ser PersonAliases",
    ):
        Person.reconstruct(
            id=PersonId.new(),
            name=PersonName("Nome da Pessoa"),
            aliases=("Alias",),  # type: ignore[arg-type]
        )