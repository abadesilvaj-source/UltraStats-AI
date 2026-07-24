"""Entidade interna que representa uma inscrição em elenco."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ultrastats_ai.domain.shared import (
    CompetitionId,
    DomainDate,
    PersonId,
    SeasonId,
    SquadRegistrationId,
    TeamId,
)
from ultrastats_ai.domain.team.enums import (
    SquadRegistrationStatus,
)
from ultrastats_ai.domain.team.errors import (
    InvalidRegistrationPeriodError,
)


@dataclass(frozen=True, slots=True)
class SquadRegistration:
    """Representa a inscrição esportiva de uma pessoa em um elenco.

    A inscrição pertence ao agregado Team e não possui repositório
    público próprio.

    O número da camisa pertence à inscrição, pois pode variar entre
    equipes, temporadas e competições.
    """

    id: SquadRegistrationId
    team_id: TeamId
    person_id: PersonId
    competition_id: CompetitionId
    season_id: SeasonId
    status: SquadRegistrationStatus
    registration_date: DomainDate
    expiration_date: DomainDate | None = None
    shirt_number: int | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        """Valida a entidade após sua criação."""

        self.validate()

    @property
    def active(self) -> bool:
        """Indica se a inscrição permanece vigente.

        Uma inscrição é considerada ativa quando está registrada e não
        possui data de expiração.
        """

        return (
            self.status is SquadRegistrationStatus.REGISTERED
            and self.expiration_date is None
        )

    def validate(self) -> None:
        """Valida os dados e as invariantes da inscrição."""

        if not isinstance(self.id, SquadRegistrationId):
            raise TypeError(
                "id deve ser SquadRegistrationId."
            )

        if not isinstance(self.team_id, TeamId):
            raise TypeError(
                "team_id deve ser TeamId."
            )

        if not isinstance(self.person_id, PersonId):
            raise TypeError(
                "person_id deve ser PersonId."
            )

        if not isinstance(
            self.competition_id,
            CompetitionId,
        ):
            raise TypeError(
                "competition_id deve ser CompetitionId."
            )

        if not isinstance(self.season_id, SeasonId):
            raise TypeError(
                "season_id deve ser SeasonId."
            )

        if not isinstance(
            self.status,
            SquadRegistrationStatus,
        ):
            raise TypeError(
                "status deve ser SquadRegistrationStatus."
            )

        if not isinstance(
            self.registration_date,
            DomainDate,
        ):
            raise TypeError(
                "registration_date deve ser DomainDate."
            )

        if (
            self.expiration_date is not None
            and not isinstance(
                self.expiration_date,
                DomainDate,
            )
        ):
            raise TypeError(
                "expiration_date deve ser DomainDate ou None."
            )

        if (
            self.shirt_number is not None
            and (
                not isinstance(self.shirt_number, int)
                or isinstance(self.shirt_number, bool)
            )
        ):
            raise TypeError(
                "shirt_number deve ser int ou None."
            )

        if (
            self.shirt_number is not None
            and self.shirt_number <= 0
        ):
            raise ValueError(
                "shirt_number deve ser maior que zero."
            )

        if (
            self.notes is not None
            and not isinstance(self.notes, str)
        ):
            raise TypeError(
                "notes deve ser str ou None."
            )

        if (
            self.expiration_date is not None
            and self.expiration_date.value
            < self.registration_date.value
        ):
            raise InvalidRegistrationPeriodError(
                "A data de expiração não pode ser anterior "
                "à data de inscrição."
            )

    def change_status(
        self,
        status: SquadRegistrationStatus,
    ) -> SquadRegistration:
        """Retorna a inscrição com um novo status."""

        if not isinstance(
            status,
            SquadRegistrationStatus,
        ):
            raise TypeError(
                "status deve ser SquadRegistrationStatus."
            )

        return replace(
            self,
            status=status,
        )

    def change_shirt_number(
        self,
        shirt_number: int | None,
    ) -> SquadRegistration:
        """Retorna a inscrição com um novo número de camisa."""

        if (
            shirt_number is not None
            and (
                not isinstance(shirt_number, int)
                or isinstance(shirt_number, bool)
            )
        ):
            raise TypeError(
                "shirt_number deve ser int ou None."
            )

        if (
            shirt_number is not None
            and shirt_number <= 0
        ):
            raise ValueError(
                "shirt_number deve ser maior que zero."
            )

        return replace(
            self,
            shirt_number=shirt_number,
        )

    def expire(
        self,
        expiration_date: DomainDate,
    ) -> SquadRegistration:
        """Define a data de expiração da inscrição.

        O método não altera automaticamente o status. A alteração de estado
        poderá ser coordenada pelo agregado Team.
        """

        if not isinstance(
            expiration_date,
            DomainDate,
        ):
            raise TypeError(
                "expiration_date deve ser DomainDate."
            )

        return replace(
            self,
            expiration_date=expiration_date,
        )

    @classmethod
    def reconstruct(
        cls,
        *,
        id: SquadRegistrationId,
        team_id: TeamId,
        person_id: PersonId,
        competition_id: CompetitionId,
        season_id: SeasonId,
        status: SquadRegistrationStatus,
        registration_date: DomainDate,
        expiration_date: DomainDate | None = None,
        shirt_number: int | None = None,
        notes: str | None = None,
    ) -> SquadRegistration:
        """Reconstrói uma inscrição recuperada da persistência."""

        return cls(
            id=id,
            team_id=team_id,
            person_id=person_id,
            competition_id=competition_id,
            season_id=season_id,
            status=status,
            registration_date=registration_date,
            expiration_date=expiration_date,
            shirt_number=shirt_number,
            notes=notes,
        )