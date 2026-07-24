"""Testes da entidade interna Referee."""

from dataclasses import FrozenInstanceError

import pytest

from ultrastats_ai.domain.people import (
    InvalidProfessionalPeriodError,
    InvalidRetirementStateError,
    Referee,
    RefereeCategory,
    RefereeRole,
    RefereeStatus,
)
from ultrastats_ai.domain.shared import (
    DomainDate,
    PersonId,
    RefereeId,
)


def make_referee(
    *,
    id: RefereeId | object | None = None,
    person_id: PersonId | object | None = None,
    primary_role: RefereeRole | object = (
        RefereeRole.MAIN_REFEREE
    ),
    category: RefereeCategory | object | None = None,
    status: RefereeStatus | object = RefereeStatus.ACTIVE,
    professional_debut_date: DomainDate | object | None = None,
    international_debut_date: DomainDate | object | None = None,
    retirement_date: DomainDate | object | None = None,
    is_international: bool | object = False,
    is_retired: bool | object = False,
    is_active: bool | object = True,
) -> Referee:
    return Referee(
        id=RefereeId.new() if id is None else id,
        person_id=(
            PersonId.new()
            if person_id is None
            else person_id
        ),
        primary_role=primary_role,
        category=category,
        status=status,
        professional_debut_date=professional_debut_date,
        international_debut_date=international_debut_date,
        retirement_date=retirement_date,
        is_international=is_international,
        is_retired=is_retired,
        is_active=is_active,
    )


def test_referee_is_created() -> None:
    referee = make_referee()

    assert isinstance(referee.id, RefereeId)
    assert isinstance(referee.person_id, PersonId)
    assert referee.primary_role is RefereeRole.MAIN_REFEREE
    assert referee.status is RefereeStatus.ACTIVE


def test_referee_rejects_invalid_identity() -> None:
    with pytest.raises(TypeError):
        make_referee(id="invalid")

    with pytest.raises(TypeError):
        make_referee(person_id="invalid")


def test_referee_rejects_invalid_role_category_and_status() -> None:
    with pytest.raises(TypeError):
        make_referee(primary_role="main_referee")

    with pytest.raises(TypeError):
        make_referee(category="international")

    with pytest.raises(TypeError):
        make_referee(status="active")


def test_referee_rejects_invalid_dates() -> None:
    with pytest.raises(TypeError):
        make_referee(
            professional_debut_date="2020-01-01"
        )

    with pytest.raises(TypeError):
        make_referee(
            international_debut_date="2021-01-01"
        )

    with pytest.raises(TypeError):
        make_referee(
            retirement_date="2040-01-01"
        )


def test_referee_rejects_international_debut_before_debut() -> None:
    with pytest.raises(
        InvalidProfessionalPeriodError
    ):
        make_referee(
            professional_debut_date=DomainDate(
                "2020-01-01"
            ),
            international_debut_date=DomainDate(
                "2019-01-01"
            ),
        )


def test_referee_rejects_retirement_before_debut() -> None:
    with pytest.raises(
        InvalidProfessionalPeriodError
    ):
        make_referee(
            professional_debut_date=DomainDate(
                "2020-01-01"
            ),
            retirement_date=DomainDate(
                "2019-01-01"
            ),
        )


def test_referee_rejects_inconsistent_retirement() -> None:
    with pytest.raises(
        InvalidRetirementStateError
    ):
        make_referee(
            status=RefereeStatus.ACTIVE,
            is_retired=True,
        )

    with pytest.raises(
        InvalidRetirementStateError
    ):
        make_referee(
            status=RefereeStatus.RETIRED,
            is_retired=False,
        )


def test_referee_changes_role_and_category(
    referee: Referee,
) -> None:
    changed_role = referee.change_role(
        RefereeRole.VIDEO_ASSISTANT_REFEREE
    )

    changed_category = changed_role.change_category(
        RefereeCategory.INTERNATIONAL
    )

    assert (
        changed_role.primary_role
        is RefereeRole.VIDEO_ASSISTANT_REFEREE
    )
    assert (
        changed_category.category
        is RefereeCategory.INTERNATIONAL
    )


def test_referee_changes_status(
    referee: Referee,
) -> None:
    updated = referee.change_status(
        RefereeStatus.TEMPORARILY_UNAVAILABLE
    )

    assert (
        updated.status
        is RefereeStatus.TEMPORARILY_UNAVAILABLE
    )


def test_referee_marks_and_clears_international_status(
    referee: Referee,
) -> None:
    international = referee.mark_international(
        "FIFA"
    )

    cleared = international.clear_international_status()

    assert international.is_international is True
    assert international.international_badge == "FIFA"
    assert cleared.is_international is False
    assert cleared.international_badge is None


def test_referee_retires_and_reactivates(
    referee: Referee,
) -> None:
    retired = referee.retire(
        DomainDate("2040-01-01")
    )

    reactivated = retired.reactivate()

    assert retired.status is RefereeStatus.RETIRED
    assert retired.is_retired is True
    assert reactivated.status is RefereeStatus.ACTIVE
    assert reactivated.is_retired is False


def test_referee_reactivate_rejects_retired_status(
    referee: Referee,
) -> None:
    retired = referee.retire()

    with pytest.raises(
        InvalidRetirementStateError
    ):
        retired.reactivate(RefereeStatus.RETIRED)


def test_referee_can_be_deactivated_and_activated(
    referee: Referee,
) -> None:
    inactive = referee.deactivate()
    active = inactive.activate()

    assert inactive.is_active is False
    assert active.is_active is True


def test_referee_equality_is_based_on_id(
    referee: Referee,
) -> None:
    assert referee == referee.deactivate()
    assert hash(referee) == hash(referee.id)


def test_referee_is_not_equal_to_other_type(
    referee: Referee,
) -> None:
    assert referee != object()


def test_referee_is_immutable(
    referee: Referee,
) -> None:
    with pytest.raises(FrozenInstanceError):
        referee.status = RefereeStatus.RETIRED