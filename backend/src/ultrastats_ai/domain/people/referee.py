"""Entidade interna Referee do agregado Person."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ultrastats_ai.domain.people.enums import (
    RefereeCategory,
    RefereeRole,
    RefereeStatus,
)
from ultrastats_ai.domain.people.errors import (
    InvalidProfessionalPeriodError,
    InvalidRetirementStateError,
)
from ultrastats_ai.domain.shared import (
    DomainDate,
    PersonId,
    RefereeId,
)


@dataclass(frozen=True, slots=True, eq=False)
class Referee:
    """Representa o perfil profissional de arbitragem."""

    id: RefereeId
    person_id: PersonId
    primary_role: RefereeRole = RefereeRole.UNKNOWN
    category: RefereeCategory | None = None
    status: RefereeStatus = RefereeStatus.UNKNOWN
    federation_name: str | None = None
    international_badge: str | None = None
    professional_debut_date: DomainDate | None = None
    international_debut_date: DomainDate | None = None
    retirement_date: DomainDate | None = None
    is_international: bool = False
    is_retired: bool = False
    is_active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.id, RefereeId):
            raise TypeError("id deve ser RefereeId.")

        if not isinstance(self.person_id, PersonId):
            raise TypeError("person_id deve ser PersonId.")

        if not isinstance(self.primary_role, RefereeRole):
            raise TypeError(
                "primary_role deve ser RefereeRole."
            )

        if (
            self.category is not None
            and not isinstance(
                self.category,
                RefereeCategory,
            )
        ):
            raise TypeError(
                "category deve ser RefereeCategory ou None."
            )

        if not isinstance(self.status, RefereeStatus):
            raise TypeError(
                "status deve ser RefereeStatus."
            )

        self._validate_optional_text(
            self.federation_name,
            "federation_name",
        )
        self._validate_optional_text(
            self.international_badge,
            "international_badge",
        )

        self._validate_optional_date(
            self.professional_debut_date,
            "professional_debut_date",
        )
        self._validate_optional_date(
            self.international_debut_date,
            "international_debut_date",
        )
        self._validate_optional_date(
            self.retirement_date,
            "retirement_date",
        )

        if not isinstance(self.is_international, bool):
            raise TypeError(
                "is_international deve ser bool."
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
        id: RefereeId,
        person_id: PersonId,
        primary_role: RefereeRole,
        category: RefereeCategory | None = None,
        status: RefereeStatus,
        federation_name: str | None = None,
        international_badge: str | None = None,
        professional_debut_date: DomainDate | None = None,
        international_debut_date: DomainDate | None = None,
        retirement_date: DomainDate | None = None,
        is_international: bool = False,
        is_retired: bool = False,
        is_active: bool = True,
    ) -> Referee:
        """Reconstrói um perfil de árbitro persistido."""

        return cls(
            id=id,
            person_id=person_id,
            primary_role=primary_role,
            category=category,
            status=status,
            federation_name=federation_name,
            international_badge=international_badge,
            professional_debut_date=professional_debut_date,
            international_debut_date=international_debut_date,
            retirement_date=retirement_date,
            is_international=is_international,
            is_retired=is_retired,
            is_active=is_active,
        )

    @staticmethod
    def _validate_optional_text(
        value: str | None,
        field_name: str,
    ) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError(
                f"{field_name} deve ser str ou None."
            )

        if isinstance(value, str) and not value.strip():
            raise ValueError(
                f"{field_name} não pode ser vazio."
            )

    @staticmethod
    def _validate_optional_date(
        value: DomainDate | None,
        field_name: str,
    ) -> None:
        if value is not None and not isinstance(
            value,
            DomainDate,
        ):
            raise TypeError(
                f"{field_name} deve ser DomainDate ou None."
            )

    def _validate_professional_period(self) -> None:
        if (
            self.professional_debut_date is not None
            and self.international_debut_date is not None
            and self.international_debut_date.value
            < self.professional_debut_date.value
        ):
            raise InvalidProfessionalPeriodError(
                "international_debut_date deve ser posterior "
                "ou igual a professional_debut_date."
            )

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
        if (
            self.is_retired
            and self.status is not RefereeStatus.RETIRED
        ):
            raise InvalidRetirementStateError(
                "Árbitro aposentado deve possuir status RETIRED."
            )

        if (
            self.status is RefereeStatus.RETIRED
            and not self.is_retired
        ):
            raise InvalidRetirementStateError(
                "Status RETIRED exige is_retired igual a True."
            )

    def change_role(
        self,
        primary_role: RefereeRole,
    ) -> Referee:
        """Altera a função profissional predominante."""

        if not isinstance(primary_role, RefereeRole):
            raise TypeError(
                "primary_role deve ser RefereeRole."
            )

        return replace(
            self,
            primary_role=primary_role,
        )

    def change_category(
        self,
        category: RefereeCategory | None,
    ) -> Referee:
        """Atualiza a categoria profissional."""

        return replace(
            self,
            category=category,
        )

    def change_status(
        self,
        status: RefereeStatus,
    ) -> Referee:
        """Altera o estado profissional."""

        if not isinstance(status, RefereeStatus):
            raise TypeError(
                "status deve ser RefereeStatus."
            )

        if status is RefereeStatus.RETIRED:
            return replace(
                self,
                status=status,
                is_retired=True,
            )

        if self.is_retired:
            raise InvalidRetirementStateError(
                "Árbitro aposentado deve ser reativado "
                "antes de assumir outro status."
            )

        return replace(self, status=status)

    def change_federation(
        self,
        federation_name: str | None,
    ) -> Referee:
        """Atualiza a federação principal conhecida."""

        return replace(
            self,
            federation_name=federation_name,
        )

    def mark_international(
        self,
        international_badge: str | None = None,
    ) -> Referee:
        """Marca o árbitro como internacional."""

        return replace(
            self,
            international_badge=international_badge,
            is_international=True,
        )

    def clear_international_status(self) -> Referee:
        """Remove o estado internacional atual."""

        return replace(
            self,
            international_badge=None,
            is_international=False,
        )

    def retire(
        self,
        retirement_date: DomainDate | None = None,
    ) -> Referee:
        """Registra a aposentadoria do árbitro."""

        return replace(
            self,
            status=RefereeStatus.RETIRED,
            retirement_date=retirement_date,
            is_retired=True,
        )

    def reactivate(
        self,
        status: RefereeStatus = RefereeStatus.ACTIVE,
    ) -> Referee:
        """Remove a aposentadoria e reativa a carreira."""

        if not isinstance(status, RefereeStatus):
            raise TypeError(
                "status deve ser RefereeStatus."
            )

        if status is RefereeStatus.RETIRED:
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

    def activate(self) -> Referee:
        """Ativa o perfil no domínio."""

        return replace(self, is_active=True)

    def deactivate(self) -> Referee:
        """Inativa o perfil no domínio."""

        return replace(self, is_active=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Referee):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)