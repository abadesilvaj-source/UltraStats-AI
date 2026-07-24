"""Entidade interna Player do agregado Person."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ultrastats_ai.domain.people.enums import PlayerStatus
from ultrastats_ai.domain.people.errors import (
    InvalidProfessionalPeriodError,
    InvalidRetirementStateError,
)
from ultrastats_ai.domain.shared import (
    DomainDate,
    PersonId,
    PlayerId,
    Position,
    ShortName,
)


@dataclass(frozen=True, slots=True, eq=False)
class Player:
    """Representa o perfil esportivo de jogador de uma pessoa."""

    id: PlayerId
    person_id: PersonId
    status: PlayerStatus = PlayerStatus.UNKNOWN
    primary_position: Position | None = None
    secondary_position: Position | None = None
    professional_debut_date: DomainDate | None = None
    retirement_date: DomainDate | None = None
    shirt_name: ShortName | None = None
    is_retired: bool = False
    is_active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.id, PlayerId):
            raise TypeError("id deve ser PlayerId.")

        if not isinstance(self.person_id, PersonId):
            raise TypeError("person_id deve ser PersonId.")

        if not isinstance(self.status, PlayerStatus):
            raise TypeError("status deve ser PlayerStatus.")

        if (
            self.primary_position is not None
            and not isinstance(self.primary_position, Position)
        ):
            raise TypeError(
                "primary_position deve ser Position ou None."
            )

        if (
            self.secondary_position is not None
            and not isinstance(self.secondary_position, Position)
        ):
            raise TypeError(
                "secondary_position deve ser Position ou None."
            )

        if (
            self.professional_debut_date is not None
            and not isinstance(
                self.professional_debut_date,
                DomainDate,
            )
        ):
            raise TypeError(
                "professional_debut_date deve ser "
                "DomainDate ou None."
            )

        if (
            self.retirement_date is not None
            and not isinstance(
                self.retirement_date,
                DomainDate,
            )
        ):
            raise TypeError(
                "retirement_date deve ser DomainDate ou None."
            )

        if (
            self.shirt_name is not None
            and not isinstance(self.shirt_name, ShortName)
        ):
            raise TypeError(
                "shirt_name deve ser ShortName ou None."
            )

        if not isinstance(self.is_retired, bool):
            raise TypeError("is_retired deve ser bool.")

        if not isinstance(self.is_active, bool):
            raise TypeError("is_active deve ser bool.")

        self._validate_professional_period()
        self._validate_retirement_state()

    @classmethod
    def reconstruct(
        cls,
        *,
        id: PlayerId,
        person_id: PersonId,
        status: PlayerStatus,
        primary_position: Position | None = None,
        secondary_position: Position | None = None,
        professional_debut_date: DomainDate | None = None,
        retirement_date: DomainDate | None = None,
        shirt_name: ShortName | None = None,
        is_retired: bool = False,
        is_active: bool = True,
    ) -> Player:
        """Reconstrói um perfil de jogador persistido."""

        return cls(
            id=id,
            person_id=person_id,
            status=status,
            primary_position=primary_position,
            secondary_position=secondary_position,
            professional_debut_date=professional_debut_date,
            retirement_date=retirement_date,
            shirt_name=shirt_name,
            is_retired=is_retired,
            is_active=is_active,
        )

    def _validate_professional_period(self) -> None:
        if (
            self.professional_debut_date is not None
            and self.retirement_date is not None
            and self.retirement_date.value
            < self.professional_debut_date.value
        ):
            raise InvalidProfessionalPeriodError(
                "retirement_date deve ser posterior ou igual "
                "a professional_debut_date."
            )

    def _validate_retirement_state(self) -> None:
        if self.is_retired and self.status is not PlayerStatus.RETIRED:
            raise InvalidRetirementStateError(
                "Jogador aposentado deve possuir status RETIRED."
            )

        if self.status is PlayerStatus.RETIRED and not self.is_retired:
            raise InvalidRetirementStateError(
                "Status RETIRED exige is_retired igual a True."
            )

    def change_status(
        self,
        status: PlayerStatus,
    ) -> Player:
        """Altera o estado profissional do jogador."""

        if not isinstance(status, PlayerStatus):
            raise TypeError("status deve ser PlayerStatus.")

        if status is PlayerStatus.RETIRED:
            return replace(
                self,
                status=status,
                is_retired=True,
            )

        if self.is_retired:
            raise InvalidRetirementStateError(
                "Jogador aposentado deve ser reativado "
                "antes de assumir outro status."
            )

        return replace(self, status=status)

    def change_positions(
        self,
        *,
        primary_position: Position | None,
        secondary_position: Position | None = None,
    ) -> Player:
        """Atualiza imutavelmente as posições do jogador."""

        return replace(
            self,
            primary_position=primary_position,
            secondary_position=secondary_position,
        )

    def change_shirt_name(
        self,
        shirt_name: ShortName | None,
    ) -> Player:
        """Atualiza o nome esportivo utilizado na camisa."""

        return replace(
            self,
            shirt_name=shirt_name,
        )

    def retire(
        self,
        retirement_date: DomainDate | None = None,
    ) -> Player:
        """Registra a aposentadoria do jogador."""

        return replace(
            self,
            status=PlayerStatus.RETIRED,
            retirement_date=retirement_date,
            is_retired=True,
        )

    def reactivate(
        self,
        status: PlayerStatus = PlayerStatus.PROFESSIONAL,
    ) -> Player:
        """Remove a aposentadoria e reativa a carreira."""

        if not isinstance(status, PlayerStatus):
            raise TypeError("status deve ser PlayerStatus.")

        if status is PlayerStatus.RETIRED:
            raise InvalidRetirementStateError(
                "A reativação exige status diferente de RETIRED."
            )

        return replace(
            self,
            status=status,
            retirement_date=None,
            is_retired=False,
            is_active=True,
        )

    def activate(self) -> Player:
        """Ativa o perfil no domínio."""

        return replace(self, is_active=True)

    def deactivate(self) -> Player:
        """Inativa o perfil no domínio."""

        return replace(self, is_active=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)