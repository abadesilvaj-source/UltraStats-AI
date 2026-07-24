"""Entidade interna que representa o vínculo entre pessoa e equipe."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ultrastats_ai.domain.shared import (
    DomainDate,
    PersonId,
    TeamId,
    TeamMembershipId,
)
from ultrastats_ai.domain.team.enums import (
    MembershipRole,
    MembershipStatus,
)
from ultrastats_ai.domain.team.errors import (
    InvalidMembershipPeriodError,
)


@dataclass(frozen=True, slots=True)
class TeamMembership:
    """Representa o vínculo histórico entre uma pessoa e uma equipe.

    A entidade pertence ao agregado Team e não deve possuir repositório
    público próprio.
    """

    id: TeamMembershipId
    team_id: TeamId
    person_id: PersonId
    role: MembershipRole
    status: MembershipStatus
    start_date: DomainDate
    end_date: DomainDate | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        """Valida a entidade após sua criação."""

        self.validate()

    @property
    def active(self) -> bool:
        """Indica se o vínculo permanece sem data de encerramento."""

        return self.end_date is None

    def validate(self) -> None:
        """Valida os dados e as invariantes do vínculo."""

        if not isinstance(self.id, TeamMembershipId):
            raise TypeError(
                "id deve ser TeamMembershipId."
            )

        if not isinstance(self.team_id, TeamId):
            raise TypeError(
                "team_id deve ser TeamId."
            )

        if not isinstance(self.person_id, PersonId):
            raise TypeError(
                "person_id deve ser PersonId."
            )

        if not isinstance(self.role, MembershipRole):
            raise TypeError(
                "role deve ser MembershipRole."
            )

        if not isinstance(self.status, MembershipStatus):
            raise TypeError(
                "status deve ser MembershipStatus."
            )

        if not isinstance(self.start_date, DomainDate):
            raise TypeError(
                "start_date deve ser DomainDate."
            )

        if (
            self.end_date is not None
            and not isinstance(self.end_date, DomainDate)
        ):
            raise TypeError(
                "end_date deve ser DomainDate ou None."
            )

        if (
            self.notes is not None
            and not isinstance(self.notes, str)
        ):
            raise TypeError(
                "notes deve ser str ou None."
            )

        if (
            self.end_date is not None
            and self.end_date.value < self.start_date.value
        ):
            raise InvalidMembershipPeriodError(
                "A data final não pode ser anterior à data inicial."
            )

    def close(
        self,
        end_date: DomainDate,
    ) -> TeamMembership:
        """Encerra o vínculo em determinada data.

        O método não altera automaticamente o status. A transição de status
        será coordenada posteriormente pelo agregado Team.
        """

        if not isinstance(end_date, DomainDate):
            raise TypeError(
                "end_date deve ser DomainDate."
            )

        return replace(
            self,
            end_date=end_date,
        )

    def change_role(
        self,
        role: MembershipRole,
    ) -> TeamMembership:
        """Retorna o vínculo com uma nova função."""

        if not isinstance(role, MembershipRole):
            raise TypeError(
                "role deve ser MembershipRole."
            )

        return replace(
            self,
            role=role,
        )

    def change_status(
        self,
        status: MembershipStatus,
    ) -> TeamMembership:
        """Retorna o vínculo com um novo status."""

        if not isinstance(status, MembershipStatus):
            raise TypeError(
                "status deve ser MembershipStatus."
            )

        return replace(
            self,
            status=status,
        )

    @classmethod
    def reconstruct(
        cls,
        *,
        id: TeamMembershipId,
        team_id: TeamId,
        person_id: PersonId,
        role: MembershipRole,
        status: MembershipStatus,
        start_date: DomainDate,
        end_date: DomainDate | None = None,
        notes: str | None = None,
    ) -> TeamMembership:
        """Reconstrói um vínculo persistido."""

        return cls(
            id=id,
            team_id=team_id,
            person_id=person_id,
            role=role,
            status=status,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
        )