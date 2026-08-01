"""Aggregate Root Person do People Context."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ultrastats_ai.domain.people.aliases import PersonAliases
from ultrastats_ai.domain.people.coach import Coach
from ultrastats_ai.domain.people.errors import (
    PersonAlreadyActiveError,
    PersonAlreadyInactiveError,
    PersonNameAliasConflictError,
    PersonProfileAlreadyExistsError,
    PersonProfileNotFoundError,
    PersonProfileOwnershipError,
)
from ultrastats_ai.domain.people.player import Player
from ultrastats_ai.domain.people.referee import Referee
from ultrastats_ai.domain.shared import (
    AliasValue,
    DisplayName,
    DomainDate,
    PersonId,
    PersonName,
)


@dataclass(frozen=True, slots=True, eq=False)
class Person:
    """Representa uma identidade humana no domínio."""

    id: PersonId
    name: PersonName
    display_name: DisplayName | None = None
    birth_date: DomainDate | None = None
    aliases: PersonAliases = PersonAliases()
    player: Player | None = None
    coach: Coach | None = None
    referee: Referee | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        self._validate_types()
        self._validate_aliases()
        self._validate_profile_ownership()

    @classmethod
    def reconstruct(
        cls,
        *,
        id: PersonId,
        name: PersonName,
        display_name: DisplayName | None = None,
        birth_date: DomainDate | None = None,
        aliases: PersonAliases | None = None,
        player: Player | None = None,
        coach: Coach | None = None,
        referee: Referee | None = None,
        is_active: bool = True,
    ) -> Person:
        """Reconstrói uma pessoa e seus perfis persistidos."""

        return cls(
            id=id,
            name=name,
            display_name=display_name,
            birth_date=birth_date,
            aliases=(
                PersonAliases.empty()
                if aliases is None
                else aliases
            ),
            player=player,
            coach=coach,
            referee=referee,
            is_active=is_active,
        )

    def _validate_types(self) -> None:
        if not isinstance(self.id, PersonId):
            raise TypeError("id deve ser PersonId.")

        if not isinstance(self.name, PersonName):
            raise TypeError("name deve ser PersonName.")

        if (
            self.display_name is not None
            and not isinstance(self.display_name, DisplayName)
        ):
            raise TypeError(
                "display_name deve ser DisplayName ou None."
            )

        if (
            self.birth_date is not None
            and not isinstance(self.birth_date, DomainDate)
        ):
            raise TypeError(
                "birth_date deve ser DomainDate ou None."
            )

        if not isinstance(self.aliases, PersonAliases):
            raise TypeError(
                "aliases deve ser PersonAliases."
            )

        if self.player is not None and not isinstance(
            self.player,
            Player,
        ):
            raise TypeError(
                "player deve ser Player ou None."
            )

        if self.coach is not None and not isinstance(
            self.coach,
            Coach,
        ):
            raise TypeError(
                "coach deve ser Coach ou None."
            )

        if self.referee is not None and not isinstance(
            self.referee,
            Referee,
        ):
            raise TypeError(
                "referee deve ser Referee ou None."
            )

        if not isinstance(self.is_active, bool):
            raise TypeError("is_active deve ser bool.")

    def _validate_aliases(self) -> None:
        normalized_name = self._normalize_text(
            self.name.value
        )

        for alias in self.aliases:
            if (
                self._normalize_text(alias.value)
                == normalized_name
            ):
                raise PersonNameAliasConflictError(
                    "O nome principal não pode também "
                    "existir como alias."
                )

    def _validate_profile_ownership(self) -> None:
        profiles = (
            self.player,
            self.coach,
            self.referee,
        )

        for profile in profiles:
            if (
                profile is not None
                and profile.person_id != self.id
            ):
                raise PersonProfileOwnershipError(
                    "O perfil profissional pertence "
                    "a outra pessoa."
                )

    def rename(
        self,
        name: PersonName,
    ) -> Person:
        """Altera o nome principal da pessoa."""

        if not isinstance(name, PersonName):
            raise TypeError(
                "name deve ser PersonName."
            )

        normalized_name = self._normalize_text(name.value)

        if self.aliases.contains_text(normalized_name):
            raise PersonNameAliasConflictError(
                "O novo nome principal já existe como alias."
            )

        return replace(
            self,
            name=name,
        )

    def change_display_name(
        self,
        display_name: DisplayName | None,
    ) -> Person:
        """Altera o nome público de exibição."""

        return replace(
            self,
            display_name=display_name,
        )

    def change_birth_date(
        self,
        birth_date: DomainDate | None,
    ) -> Person:
        """Altera a data de nascimento conhecida."""

        return replace(
            self,
            birth_date=birth_date,
        )

    def add_alias(
        self,
        alias: AliasValue,
    ) -> Person:
        """Adiciona um alias à pessoa."""

        if not isinstance(alias, AliasValue):
            raise TypeError(
                "alias deve ser AliasValue."
            )

        if (
            self._normalize_text(alias.value)
            == self._normalize_text(self.name.value)
        ):
            raise PersonNameAliasConflictError(
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
    ) -> Person:
        """Remove um alias da pessoa."""

        return replace(
            self,
            aliases=self.aliases.remove(alias),
        )

    def add_player(
        self,
        player: Player,
    ) -> Person:
        """Adiciona o perfil de jogador."""

        if not isinstance(player, Player):
            raise TypeError(
                "player deve ser Player."
            )

        self._ensure_profile_ownership(player.person_id)

        if self.player is not None:
            raise PersonProfileAlreadyExistsError(
                "A pessoa já possui perfil de jogador."
            )

        return replace(
            self,
            player=player,
        )

    def remove_player(self) -> Person:
        """Remove o perfil de jogador."""

        if self.player is None:
            raise PersonProfileNotFoundError(
                "A pessoa não possui perfil de jogador."
            )

        return replace(
            self,
            player=None,
        )

    def add_coach(
        self,
        coach: Coach,
    ) -> Person:
        """Adiciona o perfil de treinador."""

        if not isinstance(coach, Coach):
            raise TypeError(
                "coach deve ser Coach."
            )

        self._ensure_profile_ownership(coach.person_id)

        if self.coach is not None:
            raise PersonProfileAlreadyExistsError(
                "A pessoa já possui perfil de treinador."
            )

        return replace(
            self,
            coach=coach,
        )

    def remove_coach(self) -> Person:
        """Remove o perfil de treinador."""

        if self.coach is None:
            raise PersonProfileNotFoundError(
                "A pessoa não possui perfil de treinador."
            )

        return replace(
            self,
            coach=None,
        )

    def add_referee(
        self,
        referee: Referee,
    ) -> Person:
        """Adiciona o perfil de árbitro."""

        if not isinstance(referee, Referee):
            raise TypeError(
                "referee deve ser Referee."
            )

        self._ensure_profile_ownership(referee.person_id)

        if self.referee is not None:
            raise PersonProfileAlreadyExistsError(
                "A pessoa já possui perfil de árbitro."
            )

        return replace(
            self,
            referee=referee,
        )

    def remove_referee(self) -> Person:
        """Remove o perfil de árbitro."""

        if self.referee is None:
            raise PersonProfileNotFoundError(
                "A pessoa não possui perfil de árbitro."
            )

        return replace(
            self,
            referee=None,
        )

    def activate(self) -> Person:
        """Ativa a pessoa no domínio."""

        if self.is_active:
            raise PersonAlreadyActiveError(
                "A pessoa já está ativa."
            )

        return replace(
            self,
            is_active=True,
        )

    def deactivate(self) -> Person:
        """Inativa a pessoa no domínio."""

        if not self.is_active:
            raise PersonAlreadyInactiveError(
                "A pessoa já está inativa."
            )

        return replace(
            self,
            is_active=False,
        )

    def _ensure_profile_ownership(
        self,
        person_id: PersonId,
    ) -> None:
        if person_id != self.id:
            raise PersonProfileOwnershipError(
                "O perfil profissional pertence "
                "a outra pessoa."
            )

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(value.split()).casefold()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Person):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)