"""Entidade interna Coach do agregado Person."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ultrastats_ai.domain.people.enums import (
    CoachRole,
    CoachStatus,
)
from ultrastats_ai.domain.people.errors import (
    InvalidProfessionalPeriodError,
    InvalidRetirementStateError,
)
from ultrastats_ai.domain.shared import (
    CoachId,
    DomainDate,
    PersonId,
)


@dataclass(frozen=True, slots=True, eq=False)
class Coach:
    """Representa o perfil profissional de treinador."""

    id: CoachId
    person_id: PersonId
    role: CoachRole = CoachRole.UNKNOWN
    status: CoachStatus = CoachStatus.UNKNOWN
    coaching_license: str | None = None
    professional_debut_date: DomainDate | None = None
    retirement_date: DomainDate | None = None
    is_retired: bool = False
    is_active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.id, CoachId):
            raise TypeError("id deve ser CoachId.")

        if not isinstance(self.person_id, PersonId):
            raise TypeError("person_id deve ser PersonId.")

        if not isinstance(self.role, CoachRole):
            raise TypeError("role deve ser CoachRole.")

        if not isinstance(self.status, CoachStatus):
            raise TypeError("status deve ser CoachStatus.")

        if (
            self.coaching_license is not None
            and not isinstance(self.coaching_license, str)
        ):
            raise TypeError(
                "coaching_license deve ser str ou None."
            )

        if (
            isinstance(self.coaching_license, str)
            and not self.coaching_license.strip()
        ):
            raise ValueError(
                "coaching_license não pode ser vazia."
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
        id: CoachId,
        person_id: PersonId,
        role: CoachRole,
        status: CoachStatus,
        coaching_license: str | None = None,
        professional_debut_date: DomainDate | None = None,
        retirement_date: DomainDate | None = None,
        is_retired: bool = False,
        is_active: bool = True,
    ) -> Coach:
        """Reconstrói um perfil de treinador persistido."""

        return cls(
            id=id,
            person_id=person_id,
            role=role,
            status=status,
            coaching_license=coaching_license,
            professional_debut_date=professional_debut_date,
            retirement_date=retirement_date,
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
        if self.is_retired and self.status is not CoachStatus.RETIRED:
            raise InvalidRetirementStateError(
                "Treinador aposentado deve possuir status RETIRED."
            )

        if self.status is CoachStatus.RETIRED and not self.is_retired:
            raise InvalidRetirementStateError(
                "Status RETIRED exige is_retired igual a True."
            )

    def change_role(
        self,
        role: CoachRole,
    ) -> Coach:
        """Altera a função técnica predominante."""

        if not isinstance(role, CoachRole):
            raise TypeError("role deve ser CoachRole.")

        return replace(self, role=role)

    def change_status(
        self,
        status: CoachStatus,
    ) -> Coach:
        """Altera o estado profissional."""

        if not isinstance(status, CoachStatus):
            raise TypeError("status deve ser CoachStatus.")

        if status is CoachStatus.RETIRED:
            return replace(
                self,
                status=status,
                is_retired=True,
            )

        if self.is_retired:
            raise InvalidRetirementStateError(
                "Treinador aposentado deve ser reativado "
                "antes de assumir outro status."
            )

        return replace(self, status=status)

    def change_license(
        self,
        coaching_license: str | None,
    ) -> Coach:
        """Atualiza a licença técnica conhecida."""

        return replace(
            self,
            coaching_license=coaching_license,
        )

    def retire(
        self,
        retirement_date: DomainDate | None = None,
    ) -> Coach:
        """Registra a aposentadoria do treinador."""

        return replace(
            self,
            status=CoachStatus.RETIRED,
            retirement_date=retirement_date,
            is_retired=True,
        )

    def reactivate(
        self,
        status: CoachStatus = CoachStatus.ACTIVE,
    ) -> Coach:
        """Remove a aposentadoria e reativa a carreira."""

        if not isinstance(status, CoachStatus):
            raise TypeError("status deve ser CoachStatus.")

        if status is CoachStatus.RETIRED:
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

    def activate(self) -> Coach:
        """Ativa o perfil no domínio."""

        return replace(self, is_active=True)

    def deactivate(self) -> Coach:
        """Inativa o perfil no domínio."""

        return replace(self, is_active=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Coach):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)