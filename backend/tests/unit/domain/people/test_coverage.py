"""Testes complementares de cobertura do People Context."""

import pytest

from ultrastats_ai.domain.people import (
    Coach,
    CoachRole,
    CoachStatus,
    InvalidProfessionalPeriodError,
    InvalidRetirementStateError,
    Person,
    PersonAliases,
    PersonNameAliasConflictError,
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


# ============================================================
# Helpers
# ============================================================


def make_person(
    *,
    person_id: PersonId | None = None,
) -> Person:
    return Person(
        id=person_id or PersonId.new(),
        name=PersonName("Nome da Pessoa"),
    )


def make_player(
    *,
    person_id: PersonId | None = None,
    status: PlayerStatus = PlayerStatus.PROFESSIONAL,
    debut: DomainDate | None = None,
    retirement: DomainDate | None = None,
    is_retired: bool = False,
) -> Player:
    return Player(
        id=PlayerId.new(),
        person_id=person_id or PersonId.new(),
        status=status,
        professional_debut_date=debut,
        retirement_date=retirement,
        is_retired=is_retired,
    )


def make_coach(
    *,
    person_id: PersonId | None = None,
    status: CoachStatus = CoachStatus.ACTIVE,
    debut: DomainDate | None = None,
    retirement: DomainDate | None = None,
    is_retired: bool = False,
) -> Coach:
    return Coach(
        id=CoachId.new(),
        person_id=person_id or PersonId.new(),
        role=CoachRole.HEAD_COACH,
        status=status,
        professional_debut_date=debut,
        retirement_date=retirement,
        is_retired=is_retired,
    )


def make_referee(
    *,
    person_id: PersonId | None = None,
    status: RefereeStatus = RefereeStatus.ACTIVE,
    debut: DomainDate | None = None,
    international_debut: DomainDate | None = None,
    retirement: DomainDate | None = None,
    is_retired: bool = False,
) -> Referee:
    return Referee(
        id=RefereeId.new(),
        person_id=person_id or PersonId.new(),
        primary_role=RefereeRole.MAIN_REFEREE,
        status=status,
        professional_debut_date=debut,
        international_debut_date=international_debut,
        retirement_date=retirement,
        is_retired=is_retired,
    )


# ============================================================
# Player
# ============================================================


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("primary_position", "forward"),
        ("secondary_position", "midfielder"),
    ],
)
def test_player_rejects_invalid_positions(
    field_name: str,
    value: object,
) -> None:
    arguments = {
        "id": PlayerId.new(),
        "person_id": PersonId.new(),
        "status": PlayerStatus.PROFESSIONAL,
        field_name: value,
    }

    with pytest.raises(TypeError):
        Player(**arguments)  # type: ignore[arg-type]


def test_player_change_positions_revalidates_values() -> None:
    player = make_player()

    with pytest.raises(TypeError):
        player.change_positions(
            primary_position="forward",  # type: ignore[arg-type]
        )


def test_player_change_status_rejects_invalid_type() -> None:
    player = make_player()

    with pytest.raises(
        TypeError,
        match="status deve ser PlayerStatus",
    ):
        player.change_status("professional")  # type: ignore[arg-type]


def test_player_change_status_can_retire_player() -> None:
    player = make_player()

    retired = player.change_status(PlayerStatus.RETIRED)

    assert retired.status is PlayerStatus.RETIRED
    assert retired.is_retired is True


def test_retired_player_cannot_change_to_regular_status() -> None:
    player = make_player().retire()

    with pytest.raises(InvalidRetirementStateError):
        player.change_status(PlayerStatus.PROFESSIONAL)


def test_player_change_shirt_name_rejects_invalid_type() -> None:
    player = make_player()

    with pytest.raises(TypeError):
        player.change_shirt_name("Nome")  # type: ignore[arg-type]


def test_player_accepts_valid_shirt_name() -> None:
    player = make_player()

    updated = player.change_shirt_name(
        ShortName("Nome")
    )

    assert updated.shirt_name == ShortName("Nome")


def test_player_retire_revalidates_professional_period() -> None:
    player = make_player(
        debut=DomainDate("2020-01-01"),
    )

    with pytest.raises(InvalidProfessionalPeriodError):
        player.retire(
            DomainDate("2019-01-01")
        )

def test_player_reactivate_rejects_invalid_status_type() -> None:
    player = make_player().retire()

    with pytest.raises(
        TypeError,
        match="status deve ser PlayerStatus",
    ):
        player.reactivate("PROFESSIONAL")  # type: ignore[arg-type]
# ============================================================
# Coach
# ============================================================


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("is_retired", 1),
        ("is_active", 1),
    ],
)
def test_coach_rejects_non_boolean_flags(
    field_name: str,
    value: object,
) -> None:
    arguments = {
        "id": CoachId.new(),
        "person_id": PersonId.new(),
        "role": CoachRole.HEAD_COACH,
        "status": CoachStatus.ACTIVE,
        field_name: value,
    }

    with pytest.raises(TypeError):
        Coach(**arguments)  # type: ignore[arg-type]


def test_coach_change_role_rejects_invalid_type() -> None:
    coach = make_coach()

    with pytest.raises(
        TypeError,
        match="role deve ser CoachRole",
    ):
        coach.change_role("head_coach")  # type: ignore[arg-type]


def test_coach_change_status_rejects_invalid_type() -> None:
    coach = make_coach()

    with pytest.raises(
        TypeError,
        match="status deve ser CoachStatus",
    ):
        coach.change_status("active")  # type: ignore[arg-type]


def test_coach_change_status_can_retire_coach() -> None:
    coach = make_coach()

    retired = coach.change_status(CoachStatus.RETIRED)

    assert retired.status is CoachStatus.RETIRED
    assert retired.is_retired is True


def test_retired_coach_cannot_change_to_regular_status() -> None:
    coach = make_coach().retire()

    with pytest.raises(InvalidRetirementStateError):
        coach.change_status(CoachStatus.ACTIVE)


@pytest.mark.parametrize(
    "license_value",
    [
        123,
        "",
        "   ",
    ],
)
def test_coach_change_license_revalidates_value(
    license_value: object,
) -> None:
    coach = make_coach()

    with pytest.raises((TypeError, ValueError)):
        coach.change_license(license_value)  # type: ignore[arg-type]


def test_coach_retire_revalidates_professional_period() -> None:
    coach = make_coach(
        debut=DomainDate("2020-01-01"),
    )

    with pytest.raises(InvalidProfessionalPeriodError):
        coach.retire(
            DomainDate("2019-01-01")
        )

def test_coach_reactivate_rejects_invalid_status_type() -> None:
    coach = make_coach().retire()

    with pytest.raises(
        TypeError,
        match="status deve ser CoachStatus",
    ):
        coach.reactivate("ACTIVE")  # type: ignore[arg-type]

# ============================================================
# Referee
# ============================================================


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("federation_name", 123),
        ("international_badge", 123),
    ],
)
def test_referee_rejects_invalid_optional_text_types(
    field_name: str,
    value: object,
) -> None:
    arguments = {
        "id": RefereeId.new(),
        "person_id": PersonId.new(),
        "primary_role": RefereeRole.MAIN_REFEREE,
        "status": RefereeStatus.ACTIVE,
        field_name: value,
    }

    with pytest.raises(TypeError):
        Referee(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field_name",
    [
        "federation_name",
        "international_badge",
    ],
)
def test_referee_rejects_empty_optional_text(
    field_name: str,
) -> None:
    arguments = {
        "id": RefereeId.new(),
        "person_id": PersonId.new(),
        "primary_role": RefereeRole.MAIN_REFEREE,
        "status": RefereeStatus.ACTIVE,
        field_name: "   ",
    }

    with pytest.raises(ValueError):
        Referee(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("is_international", 1),
        ("is_retired", 1),
        ("is_active", 1),
    ],
)
def test_referee_rejects_non_boolean_flags(
    field_name: str,
    value: object,
) -> None:
    arguments = {
        "id": RefereeId.new(),
        "person_id": PersonId.new(),
        "primary_role": RefereeRole.MAIN_REFEREE,
        "status": RefereeStatus.ACTIVE,
        field_name: value,
    }

    with pytest.raises(TypeError):
        Referee(**arguments)  # type: ignore[arg-type]


def test_referee_change_role_rejects_invalid_type() -> None:
    referee = make_referee()

    with pytest.raises(
        TypeError,
        match="primary_role deve ser RefereeRole",
    ):
        referee.change_role("main_referee")  # type: ignore[arg-type]


def test_referee_change_category_revalidates_type() -> None:
    referee = make_referee()

    with pytest.raises(TypeError):
        referee.change_category(
            "international"  # type: ignore[arg-type]
        )


def test_referee_change_status_rejects_invalid_type() -> None:
    referee = make_referee()

    with pytest.raises(
        TypeError,
        match="status deve ser RefereeStatus",
    ):
        referee.change_status("active")  # type: ignore[arg-type]


def test_referee_change_status_can_retire_referee() -> None:
    referee = make_referee()

    retired = referee.change_status(
        RefereeStatus.RETIRED
    )

    assert retired.status is RefereeStatus.RETIRED
    assert retired.is_retired is True


def test_retired_referee_cannot_change_regular_status() -> None:
    referee = make_referee().retire()

    with pytest.raises(InvalidRetirementStateError):
        referee.change_status(RefereeStatus.ACTIVE)


@pytest.mark.parametrize(
    "federation_name",
    [
        123,
        "",
        "   ",
    ],
)
def test_referee_change_federation_revalidates_value(
    federation_name: object,
) -> None:
    referee = make_referee()

    with pytest.raises((TypeError, ValueError)):
        referee.change_federation(
            federation_name  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "badge",
    [
        123,
        "",
        "   ",
    ],
)
def test_referee_mark_international_revalidates_badge(
    badge: object,
) -> None:
    referee = make_referee()

    with pytest.raises((TypeError, ValueError)):
        referee.mark_international(
            badge  # type: ignore[arg-type]
        )


def test_referee_accepts_none_as_international_badge() -> None:
    referee = make_referee()

    updated = referee.mark_international()

    assert updated.is_international is True
    assert updated.international_badge is None


def test_referee_retire_revalidates_professional_period() -> None:
    referee = make_referee(
        debut=DomainDate("2020-01-01"),
    )

    with pytest.raises(InvalidProfessionalPeriodError):
        referee.retire(
            DomainDate("2019-01-01")
        )

def test_referee_reactivate_rejects_invalid_status_type() -> None:
    referee = make_referee().retire()

    with pytest.raises(
        TypeError,
        match="status deve ser RefereeStatus",
    ):
        referee.reactivate("ACTIVE")  # type: ignore[arg-type]

# ============================================================
# Person
# ============================================================


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("display_name", "Nome público"),
        ("birth_date", "1990-01-01"),
        ("aliases", ()),
        ("player", object()),
        ("coach", object()),
        ("referee", object()),
        ("is_active", 1),
    ],
)
def test_person_rejects_invalid_attribute_types(
    field_name: str,
    value: object,
) -> None:
    arguments = {
        "id": PersonId.new(),
        "name": PersonName("Nome da Pessoa"),
        field_name: value,
    }

    with pytest.raises(TypeError):
        Person(**arguments)  # type: ignore[arg-type]


def test_person_constructor_rejects_name_inside_aliases() -> None:
    aliases = PersonAliases(
        (
            AliasValue("  NOME   DA PESSOA  "),
        )
    )

    with pytest.raises(PersonNameAliasConflictError):
        Person(
            id=PersonId.new(),
            name=PersonName("Nome da Pessoa"),
            aliases=aliases,
        )


def test_person_rename_rejects_invalid_type() -> None:
    person = make_person()

    with pytest.raises(
        TypeError,
        match="name deve ser PersonName",
    ):
        person.rename("Outro Nome")  # type: ignore[arg-type]


def test_person_change_display_name_accepts_valid_value() -> None:
    person = make_person()
    display_name = DisplayName("Nome público")

    updated = person.change_display_name(
        display_name
    )

    assert updated.display_name == display_name


def test_person_change_display_name_accepts_none() -> None:
    person = Person(
        id=PersonId.new(),
        name=PersonName("Nome da Pessoa"),
        display_name=DisplayName("Nome público"),
    )

    updated = person.change_display_name(None)

    assert updated.display_name is None


def test_person_change_display_name_revalidates_type() -> None:
    person = make_person()

    with pytest.raises(TypeError):
        person.change_display_name(
            "Nome público"  # type: ignore[arg-type]
        )


def test_person_change_birth_date_accepts_valid_value() -> None:
    person = make_person()
    birth_date = DomainDate("1990-01-01")

    updated = person.change_birth_date(
        birth_date
    )

    assert updated.birth_date == birth_date


def test_person_change_birth_date_accepts_none() -> None:
    person = Person(
        id=PersonId.new(),
        name=PersonName("Nome da Pessoa"),
        birth_date=DomainDate("1990-01-01"),
    )

    updated = person.change_birth_date(None)

    assert updated.birth_date is None


def test_person_change_birth_date_revalidates_type() -> None:
    person = make_person()

    with pytest.raises(TypeError):
        person.change_birth_date(
            "1990-01-01"  # type: ignore[arg-type]
        )


def test_person_remove_alias_revalidates_type() -> None:
    person = make_person()

    with pytest.raises(TypeError):
        person.remove_alias(
            "Alias"  # type: ignore[arg-type]
        )


def test_person_add_player_rejects_invalid_type() -> None:
    person = make_person()

    with pytest.raises(
        TypeError,
        match="player deve ser Player",
    ):
        person.add_player(object())  # type: ignore[arg-type]


def test_person_add_coach_rejects_invalid_type() -> None:
    person = make_person()

    with pytest.raises(
        TypeError,
        match="coach deve ser Coach",
    ):
        person.add_coach(object())  # type: ignore[arg-type]


def test_person_add_referee_rejects_invalid_type() -> None:
    person = make_person()

    with pytest.raises(
        TypeError,
        match="referee deve ser Referee",
    ):
        person.add_referee(object())  # type: ignore[arg-type]


def test_person_rejects_foreign_coach() -> None:
    person = make_person()
    foreign_coach = make_coach(
        person_id=PersonId.new()
    )

    with pytest.raises(PersonProfileOwnershipError):
        person.add_coach(foreign_coach)


def test_person_rejects_foreign_referee() -> None:
    person = make_person()
    foreign_referee = make_referee(
        person_id=PersonId.new()
    )

    with pytest.raises(PersonProfileOwnershipError):
        person.add_referee(foreign_referee)


def test_person_constructor_accepts_profiles_with_correct_owner() -> None:
    person_id = PersonId.new()

    person = Person(
        id=person_id,
        name=PersonName("Nome da Pessoa"),
        player=make_player(person_id=person_id),
        coach=make_coach(person_id=person_id),
        referee=make_referee(person_id=person_id),
    )

    assert person.player is not None
    assert person.coach is not None
    assert person.referee is not None

# ============================================================
# Branches finais
# ============================================================


def test_person_add_alias_rejects_invalid_type() -> None:
    person = make_person()

    with pytest.raises(
        TypeError,
        match="alias deve ser AliasValue",
    ):
        person.add_alias("Alias inválido")  # type: ignore[arg-type]


def test_player_reactivate_rejects_invalid_status_type() -> None:
    player = make_player().retire()

    with pytest.raises(
        TypeError,
        match="status deve ser PlayerStatus",
    ):
        player.reactivate(
            "PROFESSIONAL"  # type: ignore[arg-type]
        )


def test_coach_reactivate_rejects_invalid_status_type() -> None:
    coach = make_coach().retire()

    with pytest.raises(
        TypeError,
        match="status deve ser CoachStatus",
    ):
        coach.reactivate(
            "ACTIVE"  # type: ignore[arg-type]
        )


def test_referee_reactivate_rejects_invalid_status_type() -> None:
    referee = make_referee().retire()

    with pytest.raises(
        TypeError,
        match="status deve ser RefereeStatus",
    ):
        referee.reactivate(
            "ACTIVE"  # type: ignore[arg-type]
        )