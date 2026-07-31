"""Testes da entidade interna SquadRegistration."""

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from ultrastats_ai.domain.shared import (
    CompetitionId,
    DomainDate,
    PersonId,
    SeasonId,
    SquadRegistrationId,
    TeamId,
)
from ultrastats_ai.domain.team import (
    InvalidRegistrationPeriodError,
    SquadRegistration,
    SquadRegistrationStatus,
)


def make_registration(
    *,
    id: SquadRegistrationId | None = None,
    team_id: TeamId | None = None,
    person_id: PersonId | None = None,
    competition_id: CompetitionId | None = None,
    season_id: SeasonId | None = None,
    status: SquadRegistrationStatus = (
        SquadRegistrationStatus.REGISTERED
    ),
    registration_date: DomainDate | None = None,
    expiration_date: DomainDate | None = None,
    shirt_number: int | None = 10,
    notes: str | None = None,
) -> SquadRegistration:
    """Cria uma inscrição válida para os testes."""

    return SquadRegistration(
        id=id or SquadRegistrationId.new(),
        team_id=team_id or TeamId.new(),
        person_id=person_id or PersonId.new(),
        competition_id=(
            competition_id or CompetitionId.new()
        ),
        season_id=season_id or SeasonId.new(),
        status=status,
        registration_date=(
            registration_date
            or DomainDate(value=date(2026, 1, 1))
        ),
        expiration_date=expiration_date,
        shirt_number=shirt_number,
        notes=notes,
    )


def test_registration_creation() -> None:
    registration_id = SquadRegistrationId.new()
    team_id = TeamId.new()
    person_id = PersonId.new()
    competition_id = CompetitionId.new()
    season_id = SeasonId.new()
    registration_date = DomainDate(
        value=date(2026, 1, 1)
    )

    registration = SquadRegistration(
        id=registration_id,
        team_id=team_id,
        person_id=person_id,
        competition_id=competition_id,
        season_id=season_id,
        status=SquadRegistrationStatus.REGISTERED,
        registration_date=registration_date,
        shirt_number=10,
    )

    assert registration.id == registration_id
    assert registration.team_id == team_id
    assert registration.person_id == person_id
    assert registration.competition_id == competition_id
    assert registration.season_id == season_id
    assert (
        registration.status
        is SquadRegistrationStatus.REGISTERED
    )
    assert registration.registration_date == registration_date
    assert registration.expiration_date is None
    assert registration.shirt_number == 10
    assert registration.notes is None


def test_registration_accepts_optional_values() -> None:
    expiration_date = DomainDate(
        value=date(2026, 12, 31)
    )

    registration = make_registration(
        expiration_date=expiration_date,
        shirt_number=None,
        notes="Inscrição sem número definido.",
    )

    assert registration.expiration_date == expiration_date
    assert registration.shirt_number is None
    assert (
        registration.notes
        == "Inscrição sem número definido."
    )


def test_registration_is_active_when_registered_without_expiration() -> None:
    registration = make_registration(
        status=SquadRegistrationStatus.REGISTERED,
        expiration_date=None,
    )

    assert registration.active


@pytest.mark.parametrize(
    "status",
    [
        SquadRegistrationStatus.PENDING,
        SquadRegistrationStatus.SUSPENDED,
        SquadRegistrationStatus.INELIGIBLE,
        SquadRegistrationStatus.WITHDRAWN,
        SquadRegistrationStatus.EXPIRED,
        SquadRegistrationStatus.UNKNOWN,
    ],
)
def test_registration_is_not_active_with_non_registered_status(
    status: SquadRegistrationStatus,
) -> None:
    registration = make_registration(
        status=status,
        expiration_date=None,
    )

    assert not registration.active


def test_registration_is_not_active_when_expired_by_date() -> None:
    registration = make_registration(
        status=SquadRegistrationStatus.REGISTERED,
        expiration_date=DomainDate(
            value=date(2026, 12, 31)
        ),
    )

    assert not registration.active


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_message"),
    [
        (
            "id",
            object(),
            "id deve ser SquadRegistrationId",
        ),
        (
            "team_id",
            object(),
            "team_id deve ser TeamId",
        ),
        (
            "person_id",
            object(),
            "person_id deve ser PersonId",
        ),
        (
            "competition_id",
            object(),
            "competition_id deve ser CompetitionId",
        ),
        (
            "season_id",
            object(),
            "season_id deve ser SeasonId",
        ),
        (
            "status",
            "registered",
            "status deve ser SquadRegistrationStatus",
        ),
        (
            "registration_date",
            date(2026, 1, 1),
            "registration_date deve ser DomainDate",
        ),
        (
            "expiration_date",
            date(2026, 12, 31),
            "expiration_date deve ser DomainDate ou None",
        ),
        (
            "shirt_number",
            "10",
            "shirt_number deve ser int ou None",
        ),
        (
            "notes",
            123,
            "notes deve ser str ou None",
        ),
    ],
)
def test_registration_rejects_invalid_field_types(
    field_name: str,
    invalid_value: object,
    expected_message: str,
) -> None:
    values = {
        "id": SquadRegistrationId.new(),
        "team_id": TeamId.new(),
        "person_id": PersonId.new(),
        "competition_id": CompetitionId.new(),
        "season_id": SeasonId.new(),
        "status": SquadRegistrationStatus.REGISTERED,
        "registration_date": DomainDate(
            value=date(2026, 1, 1)
        ),
        "expiration_date": None,
        "shirt_number": 10,
        "notes": None,
    }

    values[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=expected_message,
    ):
        SquadRegistration(
            **values,  # type: ignore[arg-type]
        )


def test_registration_rejects_boolean_shirt_number() -> None:
    with pytest.raises(
        TypeError,
        match="shirt_number deve ser int ou None",
    ):
        make_registration(
            shirt_number=True,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "shirt_number",
    [
        0,
        -1,
        -10,
    ],
)
def test_registration_rejects_non_positive_shirt_number(
    shirt_number: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="shirt_number deve ser maior que zero",
    ):
        make_registration(
            shirt_number=shirt_number,
        )


def test_registration_rejects_expiration_before_registration() -> None:
    with pytest.raises(
        InvalidRegistrationPeriodError,
        match="A data de expiração não pode ser anterior",
    ):
        make_registration(
            registration_date=DomainDate(
                value=date(2026, 2, 1)
            ),
            expiration_date=DomainDate(
                value=date(2026, 1, 31)
            ),
        )


def test_registration_accepts_equal_registration_and_expiration_dates() -> None:
    same_date = DomainDate(
        value=date(2026, 1, 1)
    )

    registration = make_registration(
        registration_date=same_date,
        expiration_date=same_date,
    )

    assert (
        registration.registration_date
        == registration.expiration_date
    )


def test_change_status_returns_new_instance() -> None:
    registration = make_registration(
        status=SquadRegistrationStatus.REGISTERED
    )

    updated = registration.change_status(
        SquadRegistrationStatus.SUSPENDED
    )

    assert updated is not registration
    assert (
        updated.status
        is SquadRegistrationStatus.SUSPENDED
    )
    assert (
        registration.status
        is SquadRegistrationStatus.REGISTERED
    )


def test_change_status_preserves_other_fields() -> None:
    registration = make_registration(
        notes="Observação original."
    )

    updated = registration.change_status(
        SquadRegistrationStatus.INELIGIBLE
    )

    assert updated.id == registration.id
    assert updated.team_id == registration.team_id
    assert updated.person_id == registration.person_id
    assert (
        updated.competition_id
        == registration.competition_id
    )
    assert updated.season_id == registration.season_id
    assert (
        updated.registration_date
        == registration.registration_date
    )
    assert (
        updated.expiration_date
        == registration.expiration_date
    )
    assert updated.shirt_number == registration.shirt_number
    assert updated.notes == registration.notes


def test_change_status_rejects_invalid_type() -> None:
    registration = make_registration()

    with pytest.raises(
        TypeError,
        match="status deve ser SquadRegistrationStatus",
    ):
        registration.change_status(
            "suspended"  # type: ignore[arg-type]
        )


def test_change_shirt_number_returns_new_instance() -> None:
    registration = make_registration(
        shirt_number=10
    )

    updated = registration.change_shirt_number(7)

    assert updated is not registration
    assert updated.shirt_number == 7
    assert registration.shirt_number == 10


def test_change_shirt_number_accepts_none() -> None:
    registration = make_registration(
        shirt_number=10
    )

    updated = registration.change_shirt_number(None)

    assert updated.shirt_number is None


@pytest.mark.parametrize(
    "invalid_value",
    [
        "10",
        10.5,
        True,
        object(),
    ],
)
def test_change_shirt_number_rejects_invalid_type(
    invalid_value: object,
) -> None:
    registration = make_registration()

    with pytest.raises(
        TypeError,
        match="shirt_number deve ser int ou None",
    ):
        registration.change_shirt_number(
            invalid_value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "shirt_number",
    [
        0,
        -1,
    ],
)
def test_change_shirt_number_rejects_non_positive_value(
    shirt_number: int,
) -> None:
    registration = make_registration()

    with pytest.raises(
        ValueError,
        match="shirt_number deve ser maior que zero",
    ):
        registration.change_shirt_number(
            shirt_number,
        )


def test_expire_returns_new_instance() -> None:
    registration = make_registration()
    expiration_date = DomainDate(
        value=date(2026, 12, 31)
    )

    updated = registration.expire(
        expiration_date
    )

    assert updated is not registration
    assert updated.expiration_date == expiration_date
    assert registration.expiration_date is None


def test_expire_preserves_other_fields() -> None:
    registration = make_registration(
        notes="Observação original."
    )

    updated = registration.expire(
        DomainDate(value=date(2026, 12, 31))
    )

    assert updated.id == registration.id
    assert updated.team_id == registration.team_id
    assert updated.person_id == registration.person_id
    assert (
        updated.competition_id
        == registration.competition_id
    )
    assert updated.season_id == registration.season_id
    assert updated.status == registration.status
    assert (
        updated.registration_date
        == registration.registration_date
    )
    assert updated.shirt_number == registration.shirt_number
    assert updated.notes == registration.notes


def test_expire_rejects_invalid_type() -> None:
    registration = make_registration()

    with pytest.raises(
        TypeError,
        match="expiration_date deve ser DomainDate",
    ):
        registration.expire(
            date(2026, 12, 31)  # type: ignore[arg-type]
        )


def test_expire_rejects_date_before_registration() -> None:
    registration = make_registration(
        registration_date=DomainDate(
            value=date(2026, 2, 1)
        )
    )

    with pytest.raises(
        InvalidRegistrationPeriodError,
    ):
        registration.expire(
            DomainDate(value=date(2026, 1, 31))
        )


def test_registration_reconstructs_persisted_data() -> None:
    registration_id = SquadRegistrationId.new()
    team_id = TeamId.new()
    person_id = PersonId.new()
    competition_id = CompetitionId.new()
    season_id = SeasonId.new()
    registration_date = DomainDate(
        value=date(2026, 1, 1)
    )
    expiration_date = DomainDate(
        value=date(2026, 12, 31)
    )

    registration = SquadRegistration.reconstruct(
        id=registration_id,
        team_id=team_id,
        person_id=person_id,
        competition_id=competition_id,
        season_id=season_id,
        status=SquadRegistrationStatus.EXPIRED,
        registration_date=registration_date,
        expiration_date=expiration_date,
        shirt_number=10,
        notes="Dados recuperados da persistência.",
    )

    assert registration.id == registration_id
    assert registration.team_id == team_id
    assert registration.person_id == person_id
    assert registration.competition_id == competition_id
    assert registration.season_id == season_id
    assert (
        registration.status
        is SquadRegistrationStatus.EXPIRED
    )
    assert registration.registration_date == registration_date
    assert registration.expiration_date == expiration_date
    assert registration.shirt_number == 10
    assert (
        registration.notes
        == "Dados recuperados da persistência."
    )


def test_registration_reconstruct_validates_data() -> None:
    with pytest.raises(TypeError):
        SquadRegistration.reconstruct(
            id=SquadRegistrationId.new(),
            team_id=TeamId.new(),
            person_id=PersonId.new(),
            competition_id=CompetitionId.new(),
            season_id=SeasonId.new(),
            status="registered",  # type: ignore[arg-type]
            registration_date=DomainDate(
                value=date(2026, 1, 1)
            ),
        )


def test_registration_equality_uses_all_fields() -> None:
    registration_id = SquadRegistrationId.new()
    team_id = TeamId.new()
    person_id = PersonId.new()
    competition_id = CompetitionId.new()
    season_id = SeasonId.new()

    first = make_registration(
        id=registration_id,
        team_id=team_id,
        person_id=person_id,
        competition_id=competition_id,
        season_id=season_id,
    )

    second = make_registration(
        id=registration_id,
        team_id=team_id,
        person_id=person_id,
        competition_id=competition_id,
        season_id=season_id,
    )

    assert first == second


def test_registration_with_different_id_is_not_equal() -> None:
    team_id = TeamId.new()
    person_id = PersonId.new()
    competition_id = CompetitionId.new()
    season_id = SeasonId.new()

    first = make_registration(
        team_id=team_id,
        person_id=person_id,
        competition_id=competition_id,
        season_id=season_id,
    )

    second = make_registration(
        team_id=team_id,
        person_id=person_id,
        competition_id=competition_id,
        season_id=season_id,
    )

    assert first != second


def test_registration_is_hashable() -> None:
    registration = make_registration()

    assert isinstance(hash(registration), int)


def test_registration_is_immutable() -> None:
    registration = make_registration()

    with pytest.raises(FrozenInstanceError):
        registration.status = (
            SquadRegistrationStatus.EXPIRED
        )