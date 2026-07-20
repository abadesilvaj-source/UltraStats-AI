"""Identificadores canônicos compartilhados pelo domínio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4

from ultrastats_ai.domain.shared.errors import DomainValidationError
from ultrastats_ai.domain.shared.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class CanonicalId(ValueObject):
    """Identificador canônico baseado em UUID.

    Identificadores canônicos são criados e controlados pelo UltraStats AI.

    Eles não devem ser substituídos por identificadores provenientes de
    providers externos.
    """

    value: UUID

    def validate(self) -> None:
        """Valida o UUID armazenado pelo identificador."""

        if not isinstance(self.value, UUID):
            raise DomainValidationError(
                "O valor de um identificador canônico deve ser um UUID."
            )

    @classmethod
    def new(cls) -> Self:
        """Cria um novo identificador canônico."""

        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> Self:
        """Cria um identificador a partir de uma representação textual.

        Args:
            value: UUID representado como texto.

        Raises:
            DomainValidationError: quando o texto não representa um UUID
                válido.
        """

        if not isinstance(value, str):
            raise DomainValidationError(
                "O identificador textual deve ser uma string."
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise DomainValidationError(
                "O identificador textual não pode ser vazio."
            )

        try:
            parsed_value = UUID(normalized_value)
        except ValueError as exc:
            raise DomainValidationError(
                f"Identificador canônico inválido: {value!r}."
            ) from exc

        return cls(value=parsed_value)

    def __str__(self) -> str:
        """Retorna a representação textual do UUID."""

        return str(self.value)


@dataclass(frozen=True, slots=True)
class EntityId(CanonicalId):
    """Identificador base para entidades canônicas."""


# Geography


@dataclass(frozen=True, slots=True)
class CountryId(EntityId):
    """Identificador canônico de país."""


@dataclass(frozen=True, slots=True)
class RegionId(EntityId):
    """Identificador canônico de região."""


@dataclass(frozen=True, slots=True)
class CityId(EntityId):
    """Identificador canônico de cidade."""


@dataclass(frozen=True, slots=True)
class VenueId(EntityId):
    """Identificador canônico de local esportivo."""


# Competition


@dataclass(frozen=True, slots=True)
class CompetitionId(EntityId):
    """Identificador canônico de competição."""


@dataclass(frozen=True, slots=True)
class SeasonId(EntityId):
    """Identificador canônico de temporada."""


@dataclass(frozen=True, slots=True)
class StageId(EntityId):
    """Identificador canônico de fase de competição."""


@dataclass(frozen=True, slots=True)
class RoundId(EntityId):
    """Identificador canônico de rodada."""


# People and teams


@dataclass(frozen=True, slots=True)
class PersonId(EntityId):
    """Identificador canônico de pessoa."""


@dataclass(frozen=True, slots=True)
class PlayerId(EntityId):
    """Identificador canônico de jogador."""


@dataclass(frozen=True, slots=True)
class CoachId(EntityId):
    """Identificador canônico de treinador."""


@dataclass(frozen=True, slots=True)
class RefereeId(EntityId):
    """Identificador canônico de árbitro."""


@dataclass(frozen=True, slots=True)
class TeamId(EntityId):
    """Identificador canônico de equipe."""


@dataclass(frozen=True, slots=True)
class TeamMembershipId(EntityId):
    """Identificador canônico de vínculo entre pessoa e equipe."""


@dataclass(frozen=True, slots=True)
class SquadRegistrationId(EntityId):
    """Identificador canônico de inscrição em elenco."""


# Matches


@dataclass(frozen=True, slots=True)
class MatchId(EntityId):
    """Identificador canônico de partida."""


@dataclass(frozen=True, slots=True)
class TieId(EntityId):
    """Identificador canônico de confronto agregado."""


@dataclass(frozen=True, slots=True)
class MatchEventId(EntityId):
    """Identificador canônico de evento de partida."""


@dataclass(frozen=True, slots=True)
class MatchRevisionId(EntityId):
    """Identificador canônico de revisão de partida."""


# Providers and identity resolution


@dataclass(frozen=True, slots=True)
class ProviderId(EntityId):
    """Identificador canônico de provider."""


@dataclass(frozen=True, slots=True)
class ExternalIdentityId(EntityId):
    """Identificador canônico de um mapeamento de identidade externa."""


@dataclass(frozen=True, slots=True)
class AliasId(EntityId):
    """Identificador canônico de alias."""


# Betting


@dataclass(frozen=True, slots=True)
class BookmakerId(EntityId):
    """Identificador canônico de bookmaker."""


@dataclass(frozen=True, slots=True)
class BettingMarketId(EntityId):
    """Identificador canônico de mercado de aposta."""


@dataclass(frozen=True, slots=True)
class BettingSelectionId(EntityId):
    """Identificador canônico de seleção de aposta."""


@dataclass(frozen=True, slots=True)
class OddId(EntityId):
    """Identificador canônico de registro de odd."""


@dataclass(frozen=True, slots=True)
class BetId(EntityId):
    """Identificador canônico de aposta registrada."""


# Statistics and prediction


@dataclass(frozen=True, slots=True)
class StatisticalModelId(EntityId):
    """Identificador canônico de modelo estatístico."""


@dataclass(frozen=True, slots=True)
class FeatureSetId(EntityId):
    """Identificador canônico de conjunto de features."""


@dataclass(frozen=True, slots=True)
class PredictionModelId(EntityId):
    """Identificador canônico de modelo preditivo."""


@dataclass(frozen=True, slots=True)
class PredictionId(EntityId):
    """Identificador canônico de previsão."""


@dataclass(frozen=True, slots=True)
class RecommendationId(EntityId):
    """Identificador canônico de recomendação."""


# Risk and bankroll


@dataclass(frozen=True, slots=True)
class PortfolioId(EntityId):
    """Identificador canônico de portfólio."""


@dataclass(frozen=True, slots=True)
class BankrollAccountId(EntityId):
    """Identificador canônico de conta de banca."""


@dataclass(frozen=True, slots=True)
class BankrollTransactionId(EntityId):
    """Identificador canônico de movimentação de banca."""