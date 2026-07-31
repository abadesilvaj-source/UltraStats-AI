"""Testes do Aggregate Root Team."""

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from ultrastats_ai.domain.shared import (
    AliasValue,
    CompetitionId,
    DisplayName,
    DomainDate,
    PersonId,
    ProperName,
    SeasonId,
    ShortName,
    SquadRegistrationId,
    TeamId,
    TeamMembershipId,
)
from ultrastats_ai.domain.team import (
    DuplicateSquadNumberError,
    InvalidTeamPeriodError,
    MembershipRole,
    MembershipStatus,
    SquadRegistration,
    SquadRegistrationAlreadyExistsError,
    SquadRegistrationNotFoundError,
    SquadRegistrationOwnershipError,
    SquadRegistrationStatus,
    Team,
    TeamAliases,
    TeamAlreadyActiveError,
    TeamAlreadyInactiveError,
    TeamMembership,
    TeamMembershipAlreadyExistsError,
    TeamMembershipNotFoundError,
    TeamMembershipOwnershipError,
    TeamNameAliasConflictError,
    TeamStatus,
    TeamType,
)


def first_team_type() -> TeamType:
    """Retorna um TeamType válido sem depender de um membro específico."""

    return next(iter(TeamType))


def first_non_active_status() -> TeamStatus:
    """Retorna um status diferente de ACTIVE."""

    return next(
        status
        for status in TeamStatus
        if status is not TeamStatus.ACTIVE
    )


def make_membership(
    *,
    team_id: TeamId,
) -> TeamMembership:
    """Cria um vínculo válido pertencente a uma equipe."""

    return TeamMembership(
        id=TeamMembershipId.new(),
        team_id=team_id,
        person_id=PersonId.new(),
        role=next(iter(MembershipRole)),
        status=next(iter(MembershipStatus)),
        start_date=DomainDate(
            value=date(2020, 1, 1)
        ),
    )


def make_registration(
    *,
    team_id: TeamId,
    id: SquadRegistrationId | None = None,
    person_id: PersonId | None = None,
    competition_id: CompetitionId | None = None,
    season_id: SeasonId | None = None,
    shirt_number: int | None = 10,
) -> SquadRegistration:
    """Cria uma inscrição válida pertencente a uma equipe."""

    return SquadRegistration(
        id=(
            SquadRegistrationId.new()
            if id is None
            else id
        ),
        team_id=team_id,
        person_id=(
            PersonId.new()
            if person_id is None
            else person_id
        ),
        competition_id=(
            CompetitionId.new()
            if competition_id is None
            else competition_id
        ),
        season_id=(
            SeasonId.new()
            if season_id is None
            else season_id
        ),
        status=next(
            iter(SquadRegistrationStatus)
        ),
        registration_date=DomainDate(
            value=date(2026, 1, 1)
        ),
        shirt_number=shirt_number,
    )


def make_team(
    *,
    id: TeamId | None = None,
    name: ProperName | None = None,
    team_type: TeamType | None = None,
    status: TeamStatus = TeamStatus.ACTIVE,
    display_name: DisplayName | None = None,
    short_name: ShortName | None = None,
    founded_on: DomainDate | None = None,
    dissolved_on: DomainDate | None = None,
    aliases: TeamAliases | None = None,
    memberships: tuple[TeamMembership, ...] = (),
    registrations: tuple[SquadRegistration, ...] = (),
) -> Team:
    """Cria uma equipe válida para os testes."""

    return Team(
        id=id or TeamId.new(),
        name=name or ProperName("São Paulo Futebol Clube"),
        team_type=team_type or first_team_type(),
        status=status,
        display_name=display_name,
        short_name=short_name,
        founded_on=founded_on,
        dissolved_on=dissolved_on,
        aliases=aliases or TeamAliases.empty(),
        memberships=memberships,
        registrations=registrations,
    )


def test_team_creation() -> None:
    team_id = TeamId.new()
    name = ProperName("São Paulo Futebol Clube")
    display_name = DisplayName("São Paulo")
    short_name = ShortName("São Paulo")
    founded_on = DomainDate(
        value=date(1930, 1, 25)
    )

    team = Team(
        id=team_id,
        name=name,
        team_type=first_team_type(),
        status=TeamStatus.ACTIVE,
        display_name=display_name,
        short_name=short_name,
        founded_on=founded_on,
    )

    assert team.id == team_id
    assert team.name == name
    assert team.display_name == display_name
    assert team.short_name == short_name
    assert team.founded_on == founded_on
    assert team.dissolved_on is None
    assert team.aliases == TeamAliases.empty()
    assert team.memberships == ()
    assert team.registrations == ()


def test_team_accepts_all_optional_fields() -> None:
    team_id = TeamId.new()
    membership = make_membership(
        team_id=team_id
    )
    registration = make_registration(
        team_id=team_id
    )

    team = make_team(
        id=team_id,
        display_name=DisplayName("São Paulo"),
        short_name=ShortName("SPFC"),
        founded_on=DomainDate(
            value=date(1930, 1, 25)
        ),
        dissolved_on=DomainDate(
            value=date(2030, 1, 25)
        ),
        memberships=(membership,),
        registrations=(registration,),
    )

    assert team.memberships == (membership,)
    assert team.registrations == (registration,)


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_message"),
    [
        (
            "id",
            object(),
            "id deve ser TeamId",
        ),
        (
            "name",
            "São Paulo",
            "name deve ser ProperName",
        ),
        (
            "team_type",
            "club",
            "team_type deve ser TeamType",
        ),
        (
            "status",
            "active",
            "status deve ser TeamStatus",
        ),
        (
            "display_name",
            "São Paulo",
            "display_name deve ser DisplayName ou None",
        ),
        (
            "short_name",
            "SPFC",
            "short_name deve ser ShortName ou None",
        ),
        (
            "founded_on",
            date(1930, 1, 25),
            "founded_on deve ser DomainDate ou None",
        ),
        (
            "dissolved_on",
            date(2030, 1, 25),
            "dissolved_on deve ser DomainDate ou None",
        ),
        (
            "aliases",
            (),
            "aliases deve ser TeamAliases",
        ),
        (
            "memberships",
            [],
            "memberships deve ser tuple",
        ),
        (
            "registrations",
            [],
            "registrations deve ser tuple",
        ),
    ],
)
def test_team_rejects_invalid_field_types(
    field_name: str,
    invalid_value: object,
    expected_message: str,
) -> None:
    values = {
        "id": TeamId.new(),
        "name": ProperName(
            "São Paulo Futebol Clube"
        ),
        "team_type": first_team_type(),
        "status": TeamStatus.ACTIVE,
        "display_name": None,
        "short_name": None,
        "founded_on": None,
        "dissolved_on": None,
        "aliases": TeamAliases.empty(),
        "memberships": (),
        "registrations": (),
    }

    values[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=expected_message,
    ):
        Team(
            **values,  # type: ignore[arg-type]
        )


def test_team_rejects_invalid_membership_item() -> None:
    with pytest.raises(
        TypeError,
        match="Todos os itens de memberships",
    ):
        make_team(
            memberships=(
                object(),  # type: ignore[arg-type]
            )
        )


def test_team_rejects_invalid_registration_item() -> None:
    with pytest.raises(
        TypeError,
        match="Todos os itens de registrations",
    ):
        make_team(
            registrations=(
                object(),  # type: ignore[arg-type]
            )
        )


def test_team_rejects_dissolution_before_foundation() -> None:
    with pytest.raises(
        InvalidTeamPeriodError,
        match="A data de dissolução não pode ser anterior",
    ):
        make_team(
            founded_on=DomainDate(
                value=date(2000, 1, 1)
            ),
            dissolved_on=DomainDate(
                value=date(1999, 12, 31)
            ),
        )


def test_team_accepts_equal_foundation_and_dissolution_dates() -> None:
    same_date = DomainDate(
        value=date(2000, 1, 1)
    )

    team = make_team(
        founded_on=same_date,
        dissolved_on=same_date,
    )

    assert team.founded_on == team.dissolved_on


def test_team_accepts_dissolution_without_known_foundation() -> None:
    dissolved_on = DomainDate(
        value=date(2000, 1, 1)
    )

    team = make_team(
        founded_on=None,
        dissolved_on=dissolved_on,
    )

    assert team.dissolved_on == dissolved_on


def test_team_rejects_name_also_used_as_alias() -> None:
    aliases = TeamAliases.from_iterable(
        [
            AliasValue(
                "  SÃO   PAULO FUTEBOL CLUBE  "
            )
        ]
    )

    with pytest.raises(
        TeamNameAliasConflictError,
        match="nome principal da equipe",
    ):
        make_team(
            name=ProperName(
                "São Paulo Futebol Clube"
            ),
            aliases=aliases,
        )


def test_team_accepts_different_alias() -> None:
    aliases = TeamAliases.from_iterable(
        [
            AliasValue("SPFC"),
        ]
    )

    team = make_team(
        aliases=aliases,
    )

    assert team.aliases == aliases


def test_team_rejects_membership_owned_by_another_team() -> None:
    membership = make_membership(
        team_id=TeamId.new()
    )

    with pytest.raises(
        TeamMembershipOwnershipError,
        match="outra equipe",
    ):
        make_team(
            id=TeamId.new(),
            memberships=(membership,),
        )


def test_team_accepts_owned_membership() -> None:
    team_id = TeamId.new()
    membership = make_membership(
        team_id=team_id
    )

    team = make_team(
        id=team_id,
        memberships=(membership,),
    )

    assert team.memberships == (membership,)


def test_team_rejects_registration_owned_by_another_team() -> None:
    registration = make_registration(
        team_id=TeamId.new()
    )

    with pytest.raises(
        SquadRegistrationOwnershipError,
        match="outra equipe",
    ):
        make_team(
            id=TeamId.new(),
            registrations=(registration,),
        )


def test_team_accepts_owned_registration() -> None:
    team_id = TeamId.new()
    registration = make_registration(
        team_id=team_id
    )

    team = make_team(
        id=team_id,
        registrations=(registration,),
    )

    assert team.registrations == (registration,)


def test_membership_count_returns_collection_size() -> None:
    team_id = TeamId.new()

    team = make_team(
        id=team_id,
        memberships=(
            make_membership(team_id=team_id),
            make_membership(team_id=team_id),
        ),
    )

    assert team.membership_count == 2


def test_registration_count_returns_collection_size() -> None:
    team_id = TeamId.new()

    team = make_team(
        id=team_id,
        registrations=(
            make_registration(team_id=team_id),
            make_registration(team_id=team_id),
        ),
    )

    assert team.registration_count == 2


def test_team_is_active_with_active_status() -> None:
    team = make_team(
        status=TeamStatus.ACTIVE
    )

    assert team.is_active


def test_team_is_not_active_with_another_status() -> None:
    team = make_team(
        status=first_non_active_status()
    )

    assert not team.is_active


def test_team_reconstructs_persisted_data() -> None:
    team_id = TeamId.new()
    membership = make_membership(
        team_id=team_id
    )
    registration = make_registration(
        team_id=team_id
    )
    aliases = TeamAliases.from_iterable(
        [
            AliasValue("SPFC"),
        ]
    )

    team = Team.reconstruct(
        id=team_id,
        name=ProperName(
            "São Paulo Futebol Clube"
        ),
        team_type=first_team_type(),
        status=TeamStatus.ACTIVE,
        display_name=DisplayName("São Paulo"),
        short_name=ShortName("SPFC"),
        founded_on=DomainDate(
            value=date(1930, 1, 25)
        ),
        aliases=aliases,
        memberships=(membership,),
        registrations=(registration,),
    )

    assert team.id == team_id
    assert team.aliases == aliases
    assert team.memberships == (membership,)
    assert team.registrations == (registration,)


def test_team_reconstruct_uses_empty_collections_by_default() -> None:
    team = Team.reconstruct(
        id=TeamId.new(),
        name=ProperName(
            "São Paulo Futebol Clube"
        ),
        team_type=first_team_type(),
        status=TeamStatus.ACTIVE,
    )

    assert team.aliases == TeamAliases.empty()
    assert team.memberships == ()
    assert team.registrations == ()


def test_team_reconstruct_validates_data() -> None:
    with pytest.raises(TypeError):
        Team.reconstruct(
            id=TeamId.new(),
            name="São Paulo",  # type: ignore[arg-type]
            team_type=first_team_type(),
            status=TeamStatus.ACTIVE,
        )


def test_team_equality_is_based_on_id() -> None:
    team_id = TeamId.new()

    first = make_team(
        id=team_id,
        name=ProperName(
            "São Paulo Futebol Clube"
        ),
    )

    second = make_team(
        id=team_id,
        name=ProperName(
            "Outro Nome de Equipe"
        ),
    )

    assert first == second


def test_teams_with_different_ids_are_not_equal() -> None:
    first = make_team()
    second = make_team()

    assert first != second


def test_team_comparison_with_other_type_returns_false() -> None:
    team = make_team()

    assert team != object()


def test_team_hash_is_based_on_id() -> None:
    team_id = TeamId.new()
    team = make_team(
        id=team_id
    )

    assert hash(team) == hash(team_id)


def test_team_is_immutable() -> None:
    team = make_team()

    with pytest.raises(FrozenInstanceError):
        team.status = first_non_active_status()

def test_contains_membership_returns_true_when_membership_exists() -> None:
    team_id = TeamId.new()
    membership = make_membership(
        team_id=team_id
    )

    team = make_team(
        id=team_id,
        memberships=(membership,),
    )

    assert team.contains_membership(
        membership.id
    )


def test_contains_membership_returns_false_when_membership_does_not_exist(
) -> None:
    team = make_team()

    assert not team.contains_membership(
        TeamMembershipId.new()
    )


def test_contains_membership_rejects_invalid_id_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="membership_id deve ser TeamMembershipId",
    ):
        team.contains_membership(
            object(),  # type: ignore[arg-type]
        )


def test_find_membership_returns_existing_membership() -> None:
    team_id = TeamId.new()
    membership = make_membership(
        team_id=team_id
    )

    team = make_team(
        id=team_id,
        memberships=(membership,),
    )

    result = team.find_membership(
        membership.id
    )

    assert result is membership


def test_find_membership_rejects_invalid_id_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="membership_id deve ser TeamMembershipId",
    ):
        team.find_membership(
            object(),  # type: ignore[arg-type]
        )


def test_find_membership_raises_when_membership_does_not_exist() -> None:
    team = make_team()

    with pytest.raises(
        TeamMembershipNotFoundError,
        match="não foi encontrado",
    ):
        team.find_membership(
            TeamMembershipId.new()
        )


def test_add_membership_returns_new_team() -> None:
    team_id = TeamId.new()
    team = make_team(
        id=team_id
    )
    membership = make_membership(
        team_id=team_id
    )

    updated = team.add_membership(
        membership
    )

    assert updated is not team
    assert updated.memberships == (
        membership,
    )
    assert team.memberships == ()


def test_add_membership_preserves_existing_memberships() -> None:
    team_id = TeamId.new()
    first = make_membership(
        team_id=team_id
    )
    second = make_membership(
        team_id=team_id
    )

    team = make_team(
        id=team_id,
        memberships=(first,),
    )

    updated = team.add_membership(
        second
    )

    assert updated.memberships == (
        first,
        second,
    )


def test_add_membership_preserves_other_team_fields() -> None:
    team_id = TeamId.new()
    team = make_team(
        id=team_id,
        display_name=DisplayName("São Paulo"),
        short_name=ShortName("SPFC"),
        founded_on=DomainDate(
            value=date(1930, 1, 25)
        ),
    )
    membership = make_membership(
        team_id=team_id
    )

    updated = team.add_membership(
        membership
    )

    assert updated.id == team.id
    assert updated.name == team.name
    assert updated.team_type == team.team_type
    assert updated.status == team.status
    assert updated.display_name == team.display_name
    assert updated.short_name == team.short_name
    assert updated.founded_on == team.founded_on
    assert updated.dissolved_on == team.dissolved_on
    assert updated.aliases == team.aliases
    assert updated.registrations == team.registrations


def test_add_membership_rejects_invalid_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="membership deve ser TeamMembership",
    ):
        team.add_membership(
            object(),  # type: ignore[arg-type]
        )


def test_add_membership_rejects_membership_from_another_team() -> None:
    team = make_team(
        id=TeamId.new()
    )
    membership = make_membership(
        team_id=TeamId.new()
    )

    with pytest.raises(
        TeamMembershipOwnershipError,
        match="outra equipe",
    ):
        team.add_membership(
            membership
        )


def test_add_membership_rejects_duplicate_id() -> None:
    team_id = TeamId.new()
    membership = make_membership(
        team_id=team_id
    )

    team = make_team(
        id=team_id,
        memberships=(membership,),
    )

    duplicate = TeamMembership.reconstruct(
        id=membership.id,
        team_id=team_id,
        person_id=PersonId.new(),
        role=next(iter(MembershipRole)),
        status=next(iter(MembershipStatus)),
        start_date=DomainDate(
            value=date(2021, 1, 1)
        ),
    )

    with pytest.raises(
        TeamMembershipAlreadyExistsError,
        match="já possui um vínculo",
    ):
        team.add_membership(
            duplicate
        )


def test_remove_membership_returns_new_team() -> None:
    team_id = TeamId.new()
    membership = make_membership(
        team_id=team_id
    )

    team = make_team(
        id=team_id,
        memberships=(membership,),
    )

    updated = team.remove_membership(
        membership.id
    )

    assert updated is not team
    assert updated.memberships == ()
    assert team.memberships == (
        membership,
    )


def test_remove_membership_removes_only_selected_membership() -> None:
    team_id = TeamId.new()
    first = make_membership(
        team_id=team_id
    )
    second = make_membership(
        team_id=team_id
    )

    team = make_team(
        id=team_id,
        memberships=(
            first,
            second,
        ),
    )

    updated = team.remove_membership(
        first.id
    )

    assert updated.memberships == (
        second,
    )


def test_remove_membership_rejects_invalid_id_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="membership_id deve ser TeamMembershipId",
    ):
        team.remove_membership(
            object(),  # type: ignore[arg-type]
        )


def test_remove_membership_raises_when_not_found() -> None:
    team = make_team()

    with pytest.raises(
        TeamMembershipNotFoundError,
    ):
        team.remove_membership(
            TeamMembershipId.new()
        )


def test_replace_membership_returns_new_team() -> None:
    team_id = TeamId.new()
    membership = make_membership(
        team_id=team_id
    )

    team = make_team(
        id=team_id,
        memberships=(membership,),
    )

    replacement = membership.change_status(
        next(
            status
            for status in MembershipStatus
            if status is not membership.status
        )
    )

    updated = team.replace_membership(
        replacement
    )

    assert updated is not team
    assert updated.memberships == (
        replacement,
    )
    assert team.memberships == (
        membership,
    )


def test_replace_membership_preserves_collection_position() -> None:
    team_id = TeamId.new()
    first = make_membership(
        team_id=team_id
    )
    second = make_membership(
        team_id=team_id
    )

    team = make_team(
        id=team_id,
        memberships=(
            first,
            second,
        ),
    )

    replacement = first.change_role(
        next(
            role
            for role in MembershipRole
            if role is not first.role
        )
    )

    updated = team.replace_membership(
        replacement
    )

    assert updated.memberships == (
        replacement,
        second,
    )


def test_replace_membership_rejects_invalid_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="membership deve ser TeamMembership",
    ):
        team.replace_membership(
            object(),  # type: ignore[arg-type]
        )


def test_replace_membership_rejects_membership_from_another_team() -> None:
    team = make_team(
        id=TeamId.new()
    )
    membership = make_membership(
        team_id=TeamId.new()
    )

    with pytest.raises(
        TeamMembershipOwnershipError,
        match="outra equipe",
    ):
        team.replace_membership(
            membership
        )


def test_replace_membership_raises_when_not_found() -> None:
    team_id = TeamId.new()
    team = make_team(
        id=team_id
    )
    membership = make_membership(
        team_id=team_id
    )

    with pytest.raises(
        TeamMembershipNotFoundError,
    ):
        team.replace_membership(
            membership
        )

def test_find_membership_searches_until_later_item() -> None:
    team_id = TeamId.new()

    first = make_membership(
        team_id=team_id,
    )

    second = make_membership(
        team_id=team_id,
    )

    team = make_team(
        id=team_id,
        memberships=(
            first,
            second,
        ),
    )

    result = team.find_membership(
        second.id,
    )

    assert result is second

def test_contains_registration_returns_true_when_exists() -> None:
    team_id = TeamId.new()
    registration = make_registration(
        team_id=team_id,
    )

    team = make_team(
        id=team_id,
        registrations=(registration,),
    )

    assert team.contains_registration(
        registration.id
    )


def test_contains_registration_returns_false_when_not_exists() -> None:
    team = make_team()

    assert not team.contains_registration(
        SquadRegistrationId.new()
    )


def test_contains_registration_rejects_invalid_id_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="registration_id deve ser SquadRegistrationId",
    ):
        team.contains_registration(
            object(),  # type: ignore[arg-type]
        )


def test_find_registration_returns_existing_registration() -> None:
    team_id = TeamId.new()
    registration = make_registration(
        team_id=team_id,
    )

    team = make_team(
        id=team_id,
        registrations=(registration,),
    )

    result = team.find_registration(
        registration.id
    )

    assert result is registration


def test_find_registration_searches_until_later_item() -> None:
    team_id = TeamId.new()

    first = make_registration(
        team_id=team_id,
        shirt_number=10,
    )

    second = make_registration(
        team_id=team_id,
        shirt_number=11,
    )

    team = make_team(
        id=team_id,
        registrations=(
            first,
            second,
        ),
    )

    result = team.find_registration(
        second.id
    )

    assert result is second


def test_find_registration_rejects_invalid_id_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="registration_id deve ser SquadRegistrationId",
    ):
        team.find_registration(
            object(),  # type: ignore[arg-type]
        )


def test_find_registration_raises_when_not_found() -> None:
    team = make_team()

    with pytest.raises(
        SquadRegistrationNotFoundError,
        match="não foi encontrada",
    ):
        team.find_registration(
            SquadRegistrationId.new()
        )


def test_add_registration_returns_new_team() -> None:
    team_id = TeamId.new()
    team = make_team(
        id=team_id
    )

    registration = make_registration(
        team_id=team_id,
    )

    updated = team.add_registration(
        registration
    )

    assert updated is not team
    assert updated.registrations == (
        registration,
    )
    assert team.registrations == ()


def test_add_registration_preserves_existing_registrations() -> None:
    team_id = TeamId.new()

    first = make_registration(
        team_id=team_id,
        shirt_number=10,
    )

    second = make_registration(
        team_id=team_id,
        shirt_number=11,
    )

    team = make_team(
        id=team_id,
        registrations=(first,),
    )

    updated = team.add_registration(
        second
    )

    assert updated.registrations == (
        first,
        second,
    )


def test_add_registration_rejects_invalid_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="registration deve ser SquadRegistration",
    ):
        team.add_registration(
            object(),  # type: ignore[arg-type]
        )


def test_add_registration_rejects_registration_from_another_team(
) -> None:
    team = make_team(
        id=TeamId.new()
    )

    registration = make_registration(
        team_id=TeamId.new(),
    )

    with pytest.raises(
        SquadRegistrationOwnershipError,
        match="outra equipe",
    ):
        team.add_registration(
            registration
        )


def test_add_registration_rejects_duplicate_id() -> None:
    team_id = TeamId.new()

    registration = make_registration(
        team_id=team_id,
    )

    team = make_team(
        id=team_id,
        registrations=(registration,),
    )

    duplicate = make_registration(
        id=registration.id,
        team_id=team_id,
        shirt_number=11,
    )

    with pytest.raises(
        SquadRegistrationAlreadyExistsError,
        match="já possui uma inscrição",
    ):
        team.add_registration(
            duplicate
        )


def test_remove_registration_returns_new_team() -> None:
    team_id = TeamId.new()

    registration = make_registration(
        team_id=team_id,
    )

    team = make_team(
        id=team_id,
        registrations=(registration,),
    )

    updated = team.remove_registration(
        registration.id
    )

    assert updated is not team
    assert updated.registrations == ()
    assert team.registrations == (
        registration,
    )


def test_remove_registration_removes_only_selected_registration(
) -> None:
    team_id = TeamId.new()

    first = make_registration(
        team_id=team_id,
        shirt_number=10,
    )

    second = make_registration(
        team_id=team_id,
        shirt_number=11,
    )

    team = make_team(
        id=team_id,
        registrations=(
            first,
            second,
        ),
    )

    updated = team.remove_registration(
        first.id
    )

    assert updated.registrations == (
        second,
    )


def test_remove_registration_rejects_invalid_id_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="registration_id deve ser SquadRegistrationId",
    ):
        team.remove_registration(
            object(),  # type: ignore[arg-type]
        )


def test_remove_registration_raises_when_not_found() -> None:
    team = make_team()

    with pytest.raises(
        SquadRegistrationNotFoundError,
    ):
        team.remove_registration(
            SquadRegistrationId.new()
        )


def test_replace_registration_returns_new_team() -> None:
    team_id = TeamId.new()

    registration = make_registration(
        team_id=team_id,
        shirt_number=10,
    )

    team = make_team(
        id=team_id,
        registrations=(registration,),
    )

    replacement = registration.change_shirt_number(
        11
    )

    updated = team.replace_registration(
        replacement
    )

    assert updated is not team
    assert updated.registrations == (
        replacement,
    )
    assert team.registrations == (
        registration,
    )


def test_replace_registration_preserves_collection_position() -> None:
    team_id = TeamId.new()

    first = make_registration(
        team_id=team_id,
        shirt_number=10,
    )

    second = make_registration(
        team_id=team_id,
        shirt_number=11,
    )

    team = make_team(
        id=team_id,
        registrations=(
            first,
            second,
        ),
    )

    replacement = first.change_shirt_number(
        12
    )

    updated = team.replace_registration(
        replacement
    )

    assert updated.registrations == (
        replacement,
        second,
    )


def test_replace_registration_rejects_invalid_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="registration deve ser SquadRegistration",
    ):
        team.replace_registration(
            object(),  # type: ignore[arg-type]
        )


def test_replace_registration_rejects_registration_from_another_team(
) -> None:
    team = make_team(
        id=TeamId.new()
    )

    registration = make_registration(
        team_id=TeamId.new(),
    )

    with pytest.raises(
        SquadRegistrationOwnershipError,
        match="outra equipe",
    ):
        team.replace_registration(
            registration
        )


def test_replace_registration_raises_when_not_found() -> None:
    team_id = TeamId.new()

    team = make_team(
        id=team_id
    )

    registration = make_registration(
        team_id=team_id,
    )

    with pytest.raises(
        SquadRegistrationNotFoundError,
    ):
        team.replace_registration(
            registration
        )

def test_add_registration_rejects_duplicate_squad_number() -> None:
    team_id = TeamId.new()
    competition_id = CompetitionId.new()
    season_id = SeasonId.new()

    first = make_registration(
        team_id=team_id,
        competition_id=competition_id,
        season_id=season_id,
        shirt_number=10,
    )

    second = make_registration(
        team_id=team_id,
        competition_id=competition_id,
        season_id=season_id,
        shirt_number=10,
    )

    team = make_team(
        id=team_id,
        registrations=(first,),
    )

    with pytest.raises(
        DuplicateSquadNumberError,
        match="número de camisa",
    ):
        team.add_registration(
            second
        )


def test_add_registration_accepts_same_number_in_different_competition(
) -> None:
    team_id = TeamId.new()
    season_id = SeasonId.new()

    first = make_registration(
        team_id=team_id,
        competition_id=CompetitionId.new(),
        season_id=season_id,
        shirt_number=10,
    )

    second = make_registration(
        team_id=team_id,
        competition_id=CompetitionId.new(),
        season_id=season_id,
        shirt_number=10,
    )

    team = make_team(
        id=team_id,
        registrations=(first,),
    )

    updated = team.add_registration(
        second
    )

    assert updated.registrations == (
        first,
        second,
    )


def test_add_registration_accepts_same_number_in_different_season(
) -> None:
    team_id = TeamId.new()
    competition_id = CompetitionId.new()

    first = make_registration(
        team_id=team_id,
        competition_id=competition_id,
        season_id=SeasonId.new(),
        shirt_number=10,
    )

    second = make_registration(
        team_id=team_id,
        competition_id=competition_id,
        season_id=SeasonId.new(),
        shirt_number=10,
    )

    team = make_team(
        id=team_id,
        registrations=(first,),
    )

    updated = team.add_registration(
        second
    )

    assert updated.registrations == (
        first,
        second,
    )


def test_add_registration_accepts_multiple_without_shirt_number(
) -> None:
    team_id = TeamId.new()
    competition_id = CompetitionId.new()
    season_id = SeasonId.new()

    first = make_registration(
        team_id=team_id,
        competition_id=competition_id,
        season_id=season_id,
        shirt_number=None,
    )

    second = make_registration(
        team_id=team_id,
        competition_id=competition_id,
        season_id=season_id,
        shirt_number=None,
    )

    team = make_team(
        id=team_id,
        registrations=(first,),
    )

    updated = team.add_registration(
        second
    )

    assert updated.registrations == (
        first,
        second,
    )


def test_replace_registration_rejects_duplicate_squad_number(
) -> None:
    team_id = TeamId.new()
    competition_id = CompetitionId.new()
    season_id = SeasonId.new()

    first = make_registration(
        team_id=team_id,
        competition_id=competition_id,
        season_id=season_id,
        shirt_number=10,
    )

    second = make_registration(
        team_id=team_id,
        competition_id=competition_id,
        season_id=season_id,
        shirt_number=11,
    )

    team = make_team(
        id=team_id,
        registrations=(
            first,
            second,
        ),
    )

    replacement = second.change_shirt_number(
        10
    )

    with pytest.raises(
        DuplicateSquadNumberError,
        match="número de camisa",
    ):
        team.replace_registration(
            replacement
        )


def test_replace_registration_accepts_own_squad_number() -> None:
    team_id = TeamId.new()

    registration = make_registration(
        team_id=team_id,
        shirt_number=10,
    )

    team = make_team(
        id=team_id,
        registrations=(registration,),
    )

    updated = team.replace_registration(
        registration
    )

    assert updated.registrations == (
        registration,
    )


def test_team_rejects_duplicate_squad_numbers_during_creation(
) -> None:
    team_id = TeamId.new()
    competition_id = CompetitionId.new()
    season_id = SeasonId.new()

    first = make_registration(
        team_id=team_id,
        competition_id=competition_id,
        season_id=season_id,
        shirt_number=10,
    )

    second = make_registration(
        team_id=team_id,
        competition_id=competition_id,
        season_id=season_id,
        shirt_number=10,
    )

    with pytest.raises(
        DuplicateSquadNumberError,
        match="número de camisa",
    ):
        make_team(
            id=team_id,
            registrations=(
                first,
                second,
            ),
        )

def test_rename_changes_name() -> None:
    team = make_team()

    updated = team.rename(
        ProperName(
            "Sport Club Corinthians Paulista"
        )
    )

    assert updated.name == ProperName(
        "Sport Club Corinthians Paulista"
    )


def test_rename_rejects_invalid_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="name deve ser ProperName",
    ):
        team.rename(  # type: ignore[arg-type]
            "Corinthians"
        )


def test_rename_rejects_existing_alias() -> None:
    aliases = TeamAliases.from_iterable(
        [
            AliasValue("SPFC"),
        ]
    )

    team = make_team(
        aliases=aliases,
    )

    with pytest.raises(
        TeamNameAliasConflictError,
    ):
        team.rename(
            ProperName(
                "SPFC"
            )
        )


def test_change_display_name() -> None:
    team = make_team()

    updated = team.change_display_name(
        DisplayName(
            "São Paulo"
        )
    )

    assert updated.display_name == DisplayName(
        "São Paulo"
    )


def test_change_short_name() -> None:
    team = make_team()

    updated = team.change_short_name(
        ShortName(
            "SPFC"
        )
    )

    assert updated.short_name == ShortName(
        "SPFC"
    )


def test_change_founded_on() -> None:
    team = make_team()

    founded = DomainDate(
        value=date(1930, 1, 25)
    )

    updated = team.change_founded_on(
        founded
    )

    assert updated.founded_on == founded


def test_change_dissolved_on() -> None:
    team = make_team()

    dissolved = DomainDate(
        value=date(2050, 1, 1)
    )

    updated = team.change_dissolved_on(
        dissolved
    )

    assert updated.dissolved_on == dissolved


def test_add_alias_returns_new_team() -> None:
    team = make_team()

    updated = team.add_alias(
        AliasValue(
            "SPFC"
        )
    )

    assert updated.aliases.contains_text(
        "SPFC"
    )


def test_add_alias_rejects_invalid_type() -> None:
    team = make_team()

    with pytest.raises(
        TypeError,
        match="alias deve ser AliasValue",
    ):
        team.add_alias(  # type: ignore[arg-type]
            "SPFC"
        )


def test_add_alias_rejects_main_name() -> None:
    team = make_team()

    with pytest.raises(
        TeamNameAliasConflictError,
    ):
        team.add_alias(
            AliasValue(
                team.name.value
            )
        )


def test_remove_alias() -> None:
    team = make_team().add_alias(
        AliasValue(
            "SPFC"
        )
    )

    updated = team.remove_alias(
        AliasValue(
            "SPFC"
        )
    )

    assert not updated.aliases.contains_text(
        "SPFC"
    )


def test_activate() -> None:
    inactive = next(
        status
        for status in TeamStatus
        if status is not TeamStatus.ACTIVE
    )

    team = make_team(
        status=inactive
    )

    updated = team.activate()

    assert updated.status is TeamStatus.ACTIVE


def test_activate_when_already_active() -> None:
    team = make_team(
        status=TeamStatus.ACTIVE
    )

    with pytest.raises(
        TeamAlreadyActiveError,
    ):
        team.activate()


def test_deactivate() -> None:
    team = make_team(
        status=TeamStatus.ACTIVE
    )

    updated = team.deactivate()

    assert updated.status is not TeamStatus.ACTIVE


def test_deactivate_when_already_inactive() -> None:
    inactive = next(
        status
        for status in TeamStatus
        if status is not TeamStatus.ACTIVE
    )

    team = make_team(
        status=inactive
    )

    with pytest.raises(
        TeamAlreadyInactiveError,
    ):
        team.deactivate()
