"""Testes da entidade interna TeamMembership."""

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from ultrastats_ai.domain.shared import (
    DomainDate,
    PersonId,
    TeamId,
    TeamMembershipId,
)
from ultrastats_ai.domain.team import (
    InvalidMembershipPeriodError,
    MembershipRole,
    MembershipStatus,
    TeamMembership,
)


def make_membership(
    *,
    id: TeamMembershipId | None = None,
    team_id: TeamId | None = None,
    person_id: PersonId | None = None,
    role: MembershipRole = MembershipRole.PLAYER,
    status: MembershipStatus = MembershipStatus.ACTIVE,
    start_date: DomainDate | None = None,
    end_date: DomainDate | None = None,
    notes: str | None = None,
) -> TeamMembership:
    """Cria um vínculo válido para os testes."""

    return TeamMembership(
        id=id or TeamMembershipId.new(),
        team_id=team_id or TeamId.new(),
        person_id=person_id or PersonId.new(),
        role=role,
        status=status,
        start_date=start_date
        or DomainDate(value=date(2020, 1, 1)),
        end_date=end_date,
        notes=notes,
    )


def test_membership_creation() -> None:
    membership_id = TeamMembershipId.new()
    team_id = TeamId.new()
    person_id = PersonId.new()
    start_date = DomainDate(value=date(2020, 1, 1))

    membership = TeamMembership(
        id=membership_id,
        team_id=team_id,
        person_id=person_id,
        role=MembershipRole.PLAYER,
        status=MembershipStatus.ACTIVE,
        start_date=start_date,
    )

    assert membership.id == membership_id
    assert membership.team_id == team_id
    assert membership.person_id == person_id
    assert membership.role is MembershipRole.PLAYER
    assert membership.status is MembershipStatus.ACTIVE
    assert membership.start_date == start_date
    assert membership.end_date is None
    assert membership.notes is None


def test_membership_accepts_optional_values() -> None:
    end_date = DomainDate(value=date(2024, 12, 31))

    membership = make_membership(
        end_date=end_date,
        notes="Vínculo encerrado ao final da temporada.",
    )

    assert membership.end_date == end_date
    assert (
        membership.notes
        == "Vínculo encerrado ao final da temporada."
    )


def test_membership_is_active_without_end_date() -> None:
    membership = make_membership()

    assert membership.active


def test_membership_is_not_active_with_end_date() -> None:
    membership = make_membership(
        end_date=DomainDate(value=date(2024, 12, 31))
    )

    assert not membership.active


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_message"),
    [
        (
            "id",
            object(),
            "id deve ser TeamMembershipId",
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
            "role",
            "player",
            "role deve ser MembershipRole",
        ),
        (
            "status",
            "active",
            "status deve ser MembershipStatus",
        ),
        (
            "start_date",
            date(2020, 1, 1),
            "start_date deve ser DomainDate",
        ),
        (
            "end_date",
            date(2024, 12, 31),
            "end_date deve ser DomainDate ou None",
        ),
        (
            "notes",
            123,
            "notes deve ser str ou None",
        ),
    ],
)
def test_membership_rejects_invalid_field_types(
    field_name: str,
    invalid_value: object,
    expected_message: str,
) -> None:
    values = {
        "id": TeamMembershipId.new(),
        "team_id": TeamId.new(),
        "person_id": PersonId.new(),
        "role": MembershipRole.PLAYER,
        "status": MembershipStatus.ACTIVE,
        "start_date": DomainDate(
            value=date(2020, 1, 1)
        ),
        "end_date": None,
        "notes": None,
    }

    values[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=expected_message,
    ):
        TeamMembership(
            **values,  # type: ignore[arg-type]
        )


def test_membership_rejects_end_date_before_start_date() -> None:
    with pytest.raises(
        InvalidMembershipPeriodError,
        match="A data final não pode ser anterior",
    ):
        make_membership(
            start_date=DomainDate(
                value=date(2024, 1, 1)
            ),
            end_date=DomainDate(
                value=date(2023, 12, 31)
            ),
        )


def test_membership_accepts_end_date_equal_to_start_date() -> None:
    membership_date = DomainDate(
        value=date(2024, 1, 1)
    )

    membership = make_membership(
        start_date=membership_date,
        end_date=membership_date,
    )

    assert membership.start_date == membership.end_date


def test_membership_close_returns_new_instance() -> None:
    membership = make_membership()
    end_date = DomainDate(value=date(2024, 12, 31))

    updated = membership.close(end_date)

    assert updated is not membership
    assert updated.end_date == end_date
    assert membership.end_date is None


def test_membership_close_preserves_other_fields() -> None:
    membership = make_membership(
        notes="Observação original."
    )

    updated = membership.close(
        DomainDate(value=date(2024, 12, 31))
    )

    assert updated.id == membership.id
    assert updated.team_id == membership.team_id
    assert updated.person_id == membership.person_id
    assert updated.role == membership.role
    assert updated.status == membership.status
    assert updated.start_date == membership.start_date
    assert updated.notes == membership.notes


def test_membership_close_rejects_invalid_type() -> None:
    membership = make_membership()

    with pytest.raises(
        TypeError,
        match="end_date deve ser DomainDate",
    ):
        membership.close(
            date(2024, 12, 31)  # type: ignore[arg-type]
        )


def test_membership_close_rejects_date_before_start() -> None:
    membership = make_membership(
        start_date=DomainDate(
            value=date(2024, 1, 1)
        )
    )

    with pytest.raises(
        InvalidMembershipPeriodError,
    ):
        membership.close(
            DomainDate(value=date(2023, 12, 31))
        )


def test_membership_change_role_returns_new_instance() -> None:
    membership = make_membership(
        role=MembershipRole.PLAYER
    )

    updated = membership.change_role(
        MembershipRole.HEAD_COACH
    )

    assert updated is not membership
    assert updated.role is MembershipRole.HEAD_COACH
    assert membership.role is MembershipRole.PLAYER


def test_membership_change_role_preserves_other_fields() -> None:
    membership = make_membership()

    updated = membership.change_role(
        MembershipRole.TECHNICAL_DIRECTOR
    )

    assert updated.id == membership.id
    assert updated.team_id == membership.team_id
    assert updated.person_id == membership.person_id
    assert updated.status == membership.status
    assert updated.start_date == membership.start_date
    assert updated.end_date == membership.end_date
    assert updated.notes == membership.notes


def test_membership_change_role_rejects_invalid_type() -> None:
    membership = make_membership()

    with pytest.raises(
        TypeError,
        match="role deve ser MembershipRole",
    ):
        membership.change_role(
            "head_coach"  # type: ignore[arg-type]
        )


def test_membership_change_status_returns_new_instance() -> None:
    membership = make_membership(
        status=MembershipStatus.ACTIVE
    )

    updated = membership.change_status(
        MembershipStatus.SUSPENDED
    )

    assert updated is not membership
    assert updated.status is MembershipStatus.SUSPENDED
    assert membership.status is MembershipStatus.ACTIVE


def test_membership_change_status_preserves_other_fields() -> None:
    membership = make_membership()

    updated = membership.change_status(
        MembershipStatus.ENDED
    )

    assert updated.id == membership.id
    assert updated.team_id == membership.team_id
    assert updated.person_id == membership.person_id
    assert updated.role == membership.role
    assert updated.start_date == membership.start_date
    assert updated.end_date == membership.end_date
    assert updated.notes == membership.notes


def test_membership_change_status_rejects_invalid_type() -> None:
    membership = make_membership()

    with pytest.raises(
        TypeError,
        match="status deve ser MembershipStatus",
    ):
        membership.change_status(
            "ended"  # type: ignore[arg-type]
        )


def test_membership_reconstructs_persisted_data() -> None:
    membership_id = TeamMembershipId.new()
    team_id = TeamId.new()
    person_id = PersonId.new()
    start_date = DomainDate(value=date(2020, 1, 1))
    end_date = DomainDate(value=date(2024, 12, 31))

    membership = TeamMembership.reconstruct(
        id=membership_id,
        team_id=team_id,
        person_id=person_id,
        role=MembershipRole.HEAD_COACH,
        status=MembershipStatus.ENDED,
        start_date=start_date,
        end_date=end_date,
        notes="Dados recuperados da persistência.",
    )

    assert membership.id == membership_id
    assert membership.team_id == team_id
    assert membership.person_id == person_id
    assert membership.role is MembershipRole.HEAD_COACH
    assert membership.status is MembershipStatus.ENDED
    assert membership.start_date == start_date
    assert membership.end_date == end_date
    assert (
        membership.notes
        == "Dados recuperados da persistência."
    )


def test_membership_reconstruct_validates_data() -> None:
    with pytest.raises(TypeError):
        TeamMembership.reconstruct(
            id=TeamMembershipId.new(),
            team_id=TeamId.new(),
            person_id=PersonId.new(),
            role="player",  # type: ignore[arg-type]
            status=MembershipStatus.ACTIVE,
            start_date=DomainDate(
                value=date(2020, 1, 1)
            ),
        )


def test_membership_equality_uses_all_fields() -> None:
    membership_id = TeamMembershipId.new()
    team_id = TeamId.new()
    person_id = PersonId.new()

    first = make_membership(
        id=membership_id,
        team_id=team_id,
        person_id=person_id,
    )

    second = make_membership(
        id=membership_id,
        team_id=team_id,
        person_id=person_id,
    )

    assert first == second


def test_membership_with_different_id_is_not_equal() -> None:
    team_id = TeamId.new()
    person_id = PersonId.new()

    first = make_membership(
        team_id=team_id,
        person_id=person_id,
    )

    second = make_membership(
        team_id=team_id,
        person_id=person_id,
    )

    assert first != second


def test_membership_is_hashable() -> None:
    membership = make_membership()

    assert isinstance(hash(membership), int)


def test_membership_is_immutable() -> None:
    membership = make_membership()

    with pytest.raises(FrozenInstanceError):
        membership.status = MembershipStatus.ENDED