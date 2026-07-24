"""Testes da entidade interna Coach."""

from dataclasses import FrozenInstanceError

import pytest

from ultrastats_ai.domain.people import (
    Coach,
    CoachRole,
    CoachStatus,
    InvalidProfessionalPeriodError,
    InvalidRetirementStateError,
)
from ultrastats_ai.domain.shared import (
    CoachId,
    DomainDate,
    PersonId,
)


def make_coach(
    *,
    id: CoachId | object | None = None,
    person_id: PersonId | object | None = None,
    role: CoachRole | object = CoachRole.HEAD_COACH,
    status: CoachStatus | object = CoachStatus.ACTIVE,
    coaching_license: str | object | None = None,
    professional_debut_date: DomainDate | object | None = None,
    retirement_date: DomainDate | object | None = None,
    is_retired: bool | object = False,
    is_active: bool | object = True,
) -> Coach:
    return Coach(
        id=CoachId.new() if id is None else id,
        person_id=(
            PersonId.new()
            if person_id is None
            else person_id
        ),
        role=role,
        status=status,
        coaching_license=coaching_license,
        professional_debut_date=professional_debut_date,
        retirement_date=retirement_date,
        is_retired=is_retired,
        is_active=is_active,
    )


def test_coach_is_created() -> None:
    coach = make_coach()

    assert isinstance(coach.id, CoachId)
    assert isinstance(coach.person_id, PersonId)
    assert coach.role is CoachRole.HEAD_COACH
    assert coach.status is CoachStatus.ACTIVE


def test_coach_rejects_invalid_identity() -> None:
    with pytest.raises(TypeError):
        make_coach(id="invalid")

    with pytest.raises(TypeError):
        make_coach(person_id="invalid")


def test_coach_rejects_invalid_role_and_status() -> None:
    with pytest.raises(TypeError):
        make_coach(role="head_coach")

    with pytest.raises(TypeError):
        make_coach(status="active")


def test_coach_rejects_invalid_or_empty_license() -> None:
    with pytest.raises(TypeError):
        make_coach(coaching_license=123)

    with pytest.raises(ValueError):
        make_coach(coaching_license="   ")


def test_coach_rejects_invalid_dates() -> None:
    with pytest.raises(TypeError):
        make_coach(
            professional_debut_date="2020-01-01"
        )

    with pytest.raises(TypeError):
        make_coach(
            retirement_date="2030-01-01"
        )


def test_coach_rejects_inverted_period() -> None:
    with pytest.raises(
        InvalidProfessionalPeriodError
    ):
        make_coach(
            professional_debut_date=DomainDate(
                "2020-01-01"
            ),
            retirement_date=DomainDate(
                "2019-01-01"
            ),
        )


def test_coach_rejects_inconsistent_retirement() -> None:
    with pytest.raises(
        InvalidRetirementStateError
    ):
        make_coach(
            status=CoachStatus.ACTIVE,
            is_retired=True,
        )

    with pytest.raises(
        InvalidRetirementStateError
    ):
        make_coach(
            status=CoachStatus.RETIRED,
            is_retired=False,
        )


def test_coach_changes_role(
    coach: Coach,
) -> None:
    updated = coach.change_role(
        CoachRole.TECHNICAL_DIRECTOR
    )

    assert updated.role is CoachRole.TECHNICAL_DIRECTOR
    assert coach.role is CoachRole.HEAD_COACH


def test_coach_changes_status(
    coach: Coach,
) -> None:
    updated = coach.change_status(
        CoachStatus.UNEMPLOYED
    )

    assert updated.status is CoachStatus.UNEMPLOYED


def test_coach_changes_license(
    coach: Coach,
) -> None:
    updated = coach.change_license(
        "UEFA PRO"
    )

    assert updated.coaching_license == "UEFA PRO"


def test_coach_retires_and_reactivates(
    coach: Coach,
) -> None:
    retired = coach.retire(
        DomainDate("2040-01-01")
    )

    reactivated = retired.reactivate()

    assert retired.status is CoachStatus.RETIRED
    assert retired.is_retired is True
    assert reactivated.status is CoachStatus.ACTIVE
    assert reactivated.is_retired is False


def test_coach_reactivate_rejects_retired_status(
    coach: Coach,
) -> None:
    retired = coach.retire()

    with pytest.raises(
        InvalidRetirementStateError
    ):
        retired.reactivate(CoachStatus.RETIRED)


def test_coach_can_be_deactivated_and_activated(
    coach: Coach,
) -> None:
    inactive = coach.deactivate()
    active = inactive.activate()

    assert inactive.is_active is False
    assert active.is_active is True


def test_coach_equality_is_based_on_id(
    coach: Coach,
) -> None:
    assert coach == coach.deactivate()
    assert hash(coach) == hash(coach.id)


def test_coach_is_not_equal_to_other_type(
    coach: Coach,
) -> None:
    assert coach != object()


def test_coach_is_immutable(
    coach: Coach,
) -> None:
    with pytest.raises(FrozenInstanceError):
        coach.status = CoachStatus.RETIRED