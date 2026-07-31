"""Aggregate Root Team do Team Context."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ultrastats_ai.domain.shared import (
    AliasValue,
    DisplayName,
    DomainDate,
    ProperName,
    ShortName,
    SquadRegistrationId,
    TeamId,
    TeamMembershipId,
)

from ultrastats_ai.domain.team.aliases import TeamAliases
from ultrastats_ai.domain.team.enums import (
    TeamStatus,
    TeamType,
)
from ultrastats_ai.domain.team.errors import (
    DuplicateSquadNumberError,
    InvalidTeamPeriodError,
    SquadRegistrationAlreadyExistsError,
    SquadRegistrationNotFoundError,
    SquadRegistrationOwnershipError,
    TeamAlreadyActiveError,
    TeamAlreadyInactiveError,
    TeamMembershipAlreadyExistsError,
    TeamMembershipNotFoundError,
    TeamMembershipOwnershipError,
    TeamNameAliasConflictError,
)

from ultrastats_ai.domain.team.membership import TeamMembership
from ultrastats_ai.domain.team.registration import SquadRegistration


@dataclass(frozen=True, slots=True, eq=False)
class Team:
    """Representa uma equipe esportiva no domínio.

    Team é o Aggregate Root do Team Context.

    A equipe controla seus aliases, vínculos profissionais e inscrições
    esportivas. As entidades internas não devem ser persistidas ou alteradas
    independentemente do Aggregate Root.
    """

    id: TeamId
    name: ProperName
    team_type: TeamType
    status: TeamStatus
    display_name: DisplayName | None = None
    short_name: ShortName | None = None
    founded_on: DomainDate | None = None
    dissolved_on: DomainDate | None = None
    aliases: TeamAliases = TeamAliases()
    memberships: tuple[TeamMembership, ...] = ()
    registrations: tuple[SquadRegistration, ...] = ()

    def __post_init__(self) -> None:
        """Valida as invariantes da equipe."""

        self._validate_types()
        self._validate_period()
        self._validate_aliases()
        self._validate_membership_ownership()
        self._validate_registration_ownership()
        self._validate_unique_squad_numbers()

    @classmethod
    def reconstruct(
        cls,
        *,
        id: TeamId,
        name: ProperName,
        team_type: TeamType,
        status: TeamStatus,
        display_name: DisplayName | None = None,
        short_name: ShortName | None = None,
        founded_on: DomainDate | None = None,
        dissolved_on: DomainDate | None = None,
        aliases: TeamAliases | None = None,
        memberships: tuple[TeamMembership, ...] | None = None,
        registrations: tuple[SquadRegistration, ...] | None = None,
    ) -> Team:
        """Reconstrói uma equipe e suas entidades internas persistidas."""

        return cls(
            id=id,
            name=name,
            team_type=team_type,
            status=status,
            display_name=display_name,
            short_name=short_name,
            founded_on=founded_on,
            dissolved_on=dissolved_on,
            aliases=(
                TeamAliases.empty()
                if aliases is None
                else aliases
            ),
            memberships=(
                ()
                if memberships is None
                else memberships
            ),
            registrations=(
                ()
                if registrations is None
                else registrations
            ),
        )

    @property
    def membership_count(self) -> int:
        """Retorna a quantidade de vínculos da equipe."""

        return len(self.memberships)

    @property
    def registration_count(self) -> int:
        """Retorna a quantidade de inscrições da equipe."""

        return len(self.registrations)

    @property
    def is_active(self) -> bool:
        """Indica se a equipe está ativa no domínio."""

        return self.status is TeamStatus.ACTIVE

    def contains_membership(
        self,
        membership_id: TeamMembershipId,
    ) -> bool:
        """Indica se a equipe possui determinado vínculo."""

        if not isinstance(
            membership_id,
            TeamMembershipId,
        ):
            raise TypeError(
                "membership_id deve ser TeamMembershipId."
            )

        return any(
            membership.id == membership_id
            for membership in self.memberships
        )

    def find_membership(
        self,
        membership_id: TeamMembershipId,
    ) -> TeamMembership:
        """Localiza um vínculo pertencente à equipe.

        Raises:
            TypeError: quando o identificador possui tipo inválido.
            TeamMembershipNotFoundError: quando o vínculo não existe.
        """

        if not isinstance(
            membership_id,
            TeamMembershipId,
        ):
            raise TypeError(
                "membership_id deve ser TeamMembershipId."
            )

        for membership in self.memberships:
            if membership.id == membership_id:
                return membership

        raise TeamMembershipNotFoundError(
            "O vínculo profissional não foi encontrado "
            "na equipe."
        )

    def add_membership(
        self,
        membership: TeamMembership,
    ) -> Team:
        """Adiciona um vínculo profissional à equipe.

        O vínculo deve possuir o mesmo identificador de equipe do
        Aggregate Root.
        """

        if not isinstance(
            membership,
            TeamMembership,
        ):
            raise TypeError(
                "membership deve ser TeamMembership."
            )

        self._ensure_membership_ownership(
            membership,
        )

        if self.contains_membership(membership.id):
            raise TeamMembershipAlreadyExistsError(
                "A equipe já possui um vínculo profissional "
                "com esse identificador."
            )

        return replace(
            self,
            memberships=(
                *self.memberships,
                membership,
            ),
        )

    def remove_membership(
        self,
        membership_id: TeamMembershipId,
    ) -> Team:
        """Remove um vínculo profissional da equipe."""

        membership = self.find_membership(
            membership_id,
        )

        return replace(
            self,
            memberships=tuple(
                current
                for current in self.memberships
                if current.id != membership.id
            ),
        )

    def replace_membership(
        self,
        membership: TeamMembership,
    ) -> Team:
        """Substitui um vínculo profissional existente.

        A substituição preserva a posição do vínculo na coleção.
        """

        if not isinstance(
            membership,
            TeamMembership,
        ):
            raise TypeError(
                "membership deve ser TeamMembership."
            )

        self._ensure_membership_ownership(
            membership,
        )

        self.find_membership(
            membership.id,
        )

        return replace(
            self,
            memberships=tuple(
                membership
                if current.id == membership.id
                else current
                for current in self.memberships
            ),
        )

    def contains_registration(
        self,
        registration_id: SquadRegistrationId,
    ) -> bool:
        """Indica se a equipe possui determinada inscrição."""

        if not isinstance(
            registration_id,
            SquadRegistrationId,
        ):
            raise TypeError(
                "registration_id deve ser SquadRegistrationId."
            )

        return any(
            registration.id == registration_id
            for registration in self.registrations
        )

    def find_registration(
        self,
        registration_id: SquadRegistrationId,
    ) -> SquadRegistration:
        """Localiza uma inscrição pertencente à equipe."""

        if not isinstance(
            registration_id,
            SquadRegistrationId,
        ):
            raise TypeError(
                "registration_id deve ser SquadRegistrationId."
            )

        for registration in self.registrations:
            if registration.id == registration_id:
                return registration

        raise SquadRegistrationNotFoundError(
            "A inscrição esportiva não foi encontrada "
            "na equipe."
        )

    def add_registration(
        self,
        registration: SquadRegistration,
    ) -> Team:
        """Adiciona uma inscrição esportiva à equipe."""

        if not isinstance(
            registration,
            SquadRegistration,
        ):
            raise TypeError(
                "registration deve ser SquadRegistration."
            )

        self._ensure_registration_ownership(
            registration,
        )

        if self.contains_registration(registration.id):
            raise SquadRegistrationAlreadyExistsError(
                "A equipe já possui uma inscrição esportiva "
                "com esse identificador."
            )

        self._ensure_unique_squad_number(
            registration,
        )

        return replace(
            self,
            registrations=(
                *self.registrations,
                registration,
            ),
        )

    def remove_registration(
        self,
        registration_id: SquadRegistrationId,
    ) -> Team:
        """Remove uma inscrição esportiva da equipe."""

        registration = self.find_registration(
            registration_id,
        )

        return replace(
            self,
            registrations=tuple(
                current
                for current in self.registrations
                if current.id != registration.id
            ),
        )

    def replace_registration(
        self,
        registration: SquadRegistration,
    ) -> Team:
        """Substitui uma inscrição esportiva existente.

        A substituição preserva a posição original da inscrição
        dentro da coleção.
        """

        if not isinstance(
            registration,
            SquadRegistration,
        ):
            raise TypeError(
                "registration deve ser SquadRegistration."
            )

        self._ensure_registration_ownership(
            registration,
        )

        self.find_registration(
            registration.id,
        )

        self._ensure_unique_squad_number(
            registration,
            ignored_registration_id=registration.id,
        )

        return replace(
            self,
            registrations=tuple(
                registration
                if current.id == registration.id
                else current
                for current in self.registrations
            ),
        )

    def rename(
        self,
        name: ProperName,
    ) -> Team:
        """Altera o nome principal da equipe."""

        if not isinstance(
            name,
            ProperName,
        ):
            raise TypeError(
                "name deve ser ProperName."
            )

        if self.aliases.contains_text(
            self._normalize_text(name.value)
        ):
            raise TeamNameAliasConflictError(
                "O novo nome principal já existe como alias."
            )

        return replace(
            self,
            name=name,
        )

    def change_display_name(
        self,
        display_name: DisplayName | None,
    ) -> Team:
        """Altera o nome público da equipe."""

        return replace(
            self,
            display_name=display_name,
        )

    def change_short_name(
        self,
        short_name: ShortName | None,
    ) -> Team:
        """Altera o nome curto."""

        return replace(
            self,
            short_name=short_name,
        )

    def change_founded_on(
        self,
        founded_on: DomainDate | None,
    ) -> Team:
        """Altera a data de fundação."""

        return replace(
            self,
            founded_on=founded_on,
        )

    def change_dissolved_on(
        self,
        dissolved_on: DomainDate | None,
    ) -> Team:
        """Altera a data de dissolução."""

        return replace(
            self,
            dissolved_on=dissolved_on,
        )

    def add_alias(
        self,
        alias: AliasValue,
    ) -> Team:
        """Adiciona um alias."""

        if not isinstance(
            alias,
            AliasValue,
        ):
            raise TypeError(
                "alias deve ser AliasValue."
            )

        if (
            self._normalize_text(alias.value)
            == self._normalize_text(self.name.value)
        ):
            raise TeamNameAliasConflictError(
                "O nome principal não pode ser adicionado "
                "como alias."
            )

        return replace(
            self,
            aliases=self.aliases.add(alias),
        )

    def remove_alias(
        self,
        alias: AliasValue,
    ) -> Team:
        """Remove um alias."""

        return replace(
            self,
            aliases=self.aliases.remove(alias),
        )

    def activate(
        self,
    ) -> Team:
        """Ativa a equipe."""

        if self.status is TeamStatus.ACTIVE:
            raise TeamAlreadyActiveError(
                "A equipe já está ativa."
            )

        return replace(
            self,
            status=TeamStatus.ACTIVE,
        )

    def deactivate(
        self,
    ) -> Team:
        """Inativa a equipe."""

        if self.status is not TeamStatus.ACTIVE:
            raise TeamAlreadyInactiveError(
                "A equipe já está inativa."
            )

        inactive = next(
            status
            for status in TeamStatus
            if status is not TeamStatus.ACTIVE
        )

        return replace(
            self,
            status=inactive,
        )

    def _ensure_membership_ownership(
        self,
        membership: TeamMembership,
    ) -> None:
        """Garante que o vínculo pertença à equipe."""

        if membership.team_id != self.id:
            raise TeamMembershipOwnershipError(
                "O vínculo profissional pertence "
                "a outra equipe."
            )

    def _ensure_registration_ownership(
        self,
        registration: SquadRegistration,
    ) -> None:
        """Garante que a inscrição pertença à equipe."""

        if registration.team_id != self.id:
            raise SquadRegistrationOwnershipError(
                "A inscrição esportiva pertence "
                "a outra equipe."
            )

    def _ensure_unique_squad_number(
        self,
        registration: SquadRegistration,
        *,
        ignored_registration_id: SquadRegistrationId | None = None,
    ) -> None:
        """Impede números de camisa duplicados no mesmo contexto.

        A unicidade considera a equipe, a competição e a temporada.
        Inscrições sem número de camisa não produzem conflito.
        """

        if registration.shirt_number is None:
            return

        for current in self.registrations:
            if (
                current.id != ignored_registration_id
                and current.competition_id
                == registration.competition_id
                and current.season_id
                == registration.season_id
                and current.shirt_number
                == registration.shirt_number
            ):
                raise DuplicateSquadNumberError(
                    "O número de camisa já está sendo utilizado "
                    "por outra inscrição da equipe na mesma "
                    "competição e temporada."
                )

    def _validate_types(self) -> None:
        """Valida os tipos dos campos da equipe."""

        if not isinstance(self.id, TeamId):
            raise TypeError(
                "id deve ser TeamId."
            )

        if not isinstance(self.name, ProperName):
            raise TypeError(
                "name deve ser ProperName."
            )

        if not isinstance(self.team_type, TeamType):
            raise TypeError(
                "team_type deve ser TeamType."
            )

        if not isinstance(self.status, TeamStatus):
            raise TypeError(
                "status deve ser TeamStatus."
            )

        if (
            self.display_name is not None
            and not isinstance(
                self.display_name,
                DisplayName,
            )
        ):
            raise TypeError(
                "display_name deve ser DisplayName ou None."
            )

        if (
            self.short_name is not None
            and not isinstance(
                self.short_name,
                ShortName,
            )
        ):
            raise TypeError(
                "short_name deve ser ShortName ou None."
            )

        if (
            self.founded_on is not None
            and not isinstance(
                self.founded_on,
                DomainDate,
            )
        ):
            raise TypeError(
                "founded_on deve ser DomainDate ou None."
            )

        if (
            self.dissolved_on is not None
            and not isinstance(
                self.dissolved_on,
                DomainDate,
            )
        ):
            raise TypeError(
                "dissolved_on deve ser DomainDate ou None."
            )

        if not isinstance(self.aliases, TeamAliases):
            raise TypeError(
                "aliases deve ser TeamAliases."
            )

        if not isinstance(self.memberships, tuple):
            raise TypeError(
                "memberships deve ser tuple."
            )

        for membership in self.memberships:
            if not isinstance(
                membership,
                TeamMembership,
            ):
                raise TypeError(
                    "Todos os itens de memberships devem ser "
                    "TeamMembership."
                )

        if not isinstance(self.registrations, tuple):
            raise TypeError(
                "registrations deve ser tuple."
            )

        for registration in self.registrations:
            if not isinstance(
                registration,
                SquadRegistration,
            ):
                raise TypeError(
                    "Todos os itens de registrations devem ser "
                    "SquadRegistration."
                )

    def _validate_period(self) -> None:
        """Valida o período de existência da equipe."""

        if (
            self.founded_on is not None
            and self.dissolved_on is not None
            and self.dissolved_on.value < self.founded_on.value
        ):
            raise InvalidTeamPeriodError(
                "A data de dissolução não pode ser anterior "
                "à data de fundação."
            )

    def _validate_aliases(self) -> None:
        """Impede que o nome principal também exista como alias."""

        normalized_name = self._normalize_text(
            self.name.value
        )

        for alias in self.aliases:
            if (
                self._normalize_text(alias.value)
                == normalized_name
            ):
                raise TeamNameAliasConflictError(
                    "O nome principal da equipe não pode também "
                    "existir como alias."
                )

    def _validate_membership_ownership(self) -> None:
        """Valida que todos os vínculos pertencem à equipe."""

        for membership in self.memberships:
            self._ensure_membership_ownership(
                membership,
            )

    def _validate_registration_ownership(self) -> None:
        """Valida que todas as inscrições pertencem à equipe."""

        for registration in self.registrations:
            self._ensure_registration_ownership(
                registration,
            )

    def _validate_unique_squad_numbers(self) -> None:
        """Valida os números de camisa das inscrições existentes."""

        for registration in self.registrations:
            self._ensure_unique_squad_number(
                registration,
                ignored_registration_id=registration.id,
            )

    @staticmethod
    def _normalize_text(value: str) -> str:
        """Normaliza texto para comparações semânticas."""

        return " ".join(value.split()).casefold()

    def __eq__(self, other: object) -> bool:
        """Compara equipes pelo identificador canônico."""

        if not isinstance(other, Team):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        """Retorna o hash baseado no identificador."""

        return hash(self.id)
