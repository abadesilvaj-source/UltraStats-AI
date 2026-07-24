"""Testes da entidade interna Player."""

from dataclasses import FrozenInstanceError

import pytest

from ultrastats_ai.domain.people import (
    InvalidProfessionalPeriodError,
    InvalidRetirementStateError,
    Player,
    PlayerStatus,
)
from ultrastats_ai.domain.shared import (
    DomainDate,
    PersonId,
    PlayerId,
    ShortName,
)


def make_player(
    *,
    id: PlayerId | object | None = None,
    person_id: PersonId | object | None = None,
    status: PlayerStatus | object = PlayerStatus.PROFESSIONAL,
    professional_debut_date: DomainDate | object | None = None,
    retirement_date: DomainDate | object | None = None,
    shirt_name: ShortName | object | None = None,
    is_retired: bool | object = False,
    is_active: bool | object = True,
) -> Player:
    return Player(
        id=PlayerId.new() if id is None else id,
        person_id=(
            PersonId.new()
            if person_id is None
            else person_id
        ),
        status=status,
        professional_debut_date=professional_debut_date,
        retirement_date=retirement_date,
        shirt_name=shirt_name,
        is_retired=is_retired,
        is_active=is_active,
    )


def test_player_is_created() -> None:
    player = make_player()

    assert isinstance(player.id, PlayerId)
    assert isinstance(player.person_id, PersonId)
    assert player.status is PlayerStatus.PROFESSIONAL
    assert player.is_retired is False
    assert player.is_active is True


def test_player_rejects_invalid_id() -> None:
    with pytest.raises(TypeError, match="id deve ser PlayerId"):
        make_player(id="invalid")


def test_player_rejects_invalid_person_id() -> None:
    with pytest.raises(
        TypeError,
        match="person_id deve ser PersonId",
    ):
        make_player(person_id="invalid")


def test_player_rejects_invalid_status() -> None:
    with pytest.raises(
        TypeError,
        match="status deve ser PlayerStatus",
    ):
        make_player(status="professional")


def test_player_rejects_invalid_debut_date() -> None:
    with pytest.raises(TypeError):
        make_player(
            professional_debut_date="2020-01-01"
        )


def test_player_rejects_invalid_retirement_date() -> None:
    with pytest.raises(TypeError):
        make_player(
            retirement_date="2030-01-01"
        )


def test_player_rejects_invalid_shirt_name() -> None:
    with pytest.raises(TypeError):
        make_player(shirt_name="Neymar")


def test_player_rejects_invalid_boolean_flags() -> None:
    with pytest.raises(TypeError):
        make_player(is_retired=1)

    with pytest.raises(TypeError):
        make_player(is_active=1)


def test_player_rejects_inverted_professional_period() -> None:
    with pytest.raises(
        InvalidProfessionalPeriodError
    ):
        make_player(
            professional_debut_date=DomainDate(
                "2020-01-01"
            ),
            retirement_date=DomainDate(
                "2019-01-01"
            ),
        )


def test_player_rejects_inconsistent_retirement_flag() -> None:
    with pytest.raises(
        InvalidRetirementStateError
    ):
        make_player(
            status=PlayerStatus.PROFESSIONAL,
            is_retired=True,
        )


def test_player_rejects_retired_status_without_flag() -> None:
    with pytest.raises(
        InvalidRetirementStateError
    ):
        make_player(
            status=PlayerStatus.RETIRED,
            is_retired=False,
        )


def test_player_changes_status_immutably(
    player: Player,
) -> None:
    updated = player.change_status(
        PlayerStatus.FREE_AGENT
    )

    assert updated is not player
    assert updated == player
    assert updated.status is PlayerStatus.FREE_AGENT
    assert player.status is PlayerStatus.PROFESSIONAL


def test_player_retires_immutably(
    player: Player,
) -> None:
    retirement_date = DomainDate("2035-01-01")

    updated = player.retire(retirement_date)

    assert updated.status is PlayerStatus.RETIRED
    assert updated.is_retired is True
    assert updated.retirement_date == retirement_date
    assert player.is_retired is False


def test_player_reactivates_immutably(
    player: Player,
) -> None:
    retired = player.retire(
        DomainDate("2035-01-01")
    )

    updated = retired.reactivate()

    assert updated.status is PlayerStatus.PROFESSIONAL
    assert updated.is_retired is False
    assert updated.retirement_date is None
    assert updated.is_active is True


def test_player_reactivate_rejects_retired_status(
    player: Player,
) -> None:
    retired = player.retire()

    with pytest.raises(
        InvalidRetirementStateError
    ):
        retired.reactivate(PlayerStatus.RETIRED)


def test_player_changes_shirt_name(
    player: Player,
) -> None:
    shirt_name = ShortName("Neymar")

    updated = player.change_shirt_name(
        shirt_name
    )

    assert updated.shirt_name == shirt_name
    assert player.shirt_name is None


def test_player_can_be_deactivated_and_activated(
    player: Player,
) -> None:
    inactive = player.deactivate()
    active = inactive.activate()

    assert inactive.is_active is False
    assert active.is_active is True


def test_player_equality_is_based_on_id(
    player: Player,
) -> None:
    updated = player.deactivate()

    assert updated == player
    assert hash(updated) == hash(player)


def test_players_with_different_ids_are_not_equal(
    player: Player,
) -> None:
    other = make_player(
        person_id=player.person_id
    )

    assert other != player


def test_player_is_not_equal_to_other_type(
    player: Player,
) -> None:
    assert player != object()


def test_player_is_immutable(
    player: Player,
) -> None:
    with pytest.raises(FrozenInstanceError):
        player.is_active = False