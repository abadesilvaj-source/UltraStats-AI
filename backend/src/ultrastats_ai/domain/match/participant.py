"""Entidade interna que representa um participante de partida."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ultrastats_ai.domain.match.enums import MatchParticipantStatus
from ultrastats_ai.domain.shared import (
    MatchId,
    MatchParticipantId,
    ParticipantRole,
    TeamId,
)


@dataclass(frozen=True, slots=True)
class MatchParticipant:
    """Representa uma equipe contextual subordinada a um Match."""

    id: MatchParticipantId
    match_id: MatchId
    team_id: TeamId | None
    role: ParticipantRole
    order: int
    status: MatchParticipantStatus = MatchParticipantStatus.EXPECTED
    score: int | None = None
    is_winner: bool = False
    is_tbd: bool = False
    placeholder_name: str | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Valida tipos e invariantes do participante."""

        if not isinstance(self.id, MatchParticipantId):
            raise TypeError("id deve ser MatchParticipantId.")
        if not isinstance(self.match_id, MatchId):
            raise TypeError("match_id deve ser MatchId.")
        if self.team_id is not None and not isinstance(self.team_id, TeamId):
            raise TypeError("team_id deve ser TeamId ou None.")
        if not isinstance(self.role, ParticipantRole):
            raise TypeError("role deve ser ParticipantRole.")
        if isinstance(self.order, bool) or not isinstance(self.order, int):
            raise TypeError("order deve ser int.")
        if self.order <= 0:
            raise ValueError("order deve ser maior que zero.")
        if not isinstance(self.status, MatchParticipantStatus):
            raise TypeError("status deve ser MatchParticipantStatus.")
        if self.score is not None:
            if isinstance(self.score, bool) or not isinstance(self.score, int):
                raise TypeError("score deve ser int ou None.")
            if self.score < 0:
                raise ValueError("score não pode ser negativo.")
        if not isinstance(self.is_winner, bool):
            raise TypeError("is_winner deve ser bool.")
        if not isinstance(self.is_tbd, bool):
            raise TypeError("is_tbd deve ser bool.")
        if (
            self.placeholder_name is not None
            and not isinstance(self.placeholder_name, str)
        ):
            raise TypeError("placeholder_name deve ser str ou None.")

        normalized_placeholder = (
            self.placeholder_name.strip()
            if self.placeholder_name is not None
            else None
        )
        if self.is_tbd:
            if self.team_id is not None:
                raise ValueError(
                    "Participante a definir não pode possuir team_id."
                )
            if not normalized_placeholder:
                raise ValueError(
                    "Participante a definir exige placeholder_name."
                )
        elif self.team_id is None:
            raise ValueError(
                "Participante definido exige team_id."
            )

        object.__setattr__(
            self,
            "placeholder_name",
            normalized_placeholder,
        )

    def assign_team(self, team_id: TeamId) -> MatchParticipant:
        """Resolve um placeholder com uma equipe canônica."""

        if not isinstance(team_id, TeamId):
            raise TypeError("team_id deve ser TeamId.")

        return replace(
            self,
            team_id=team_id,
            is_tbd=False,
            placeholder_name=None,
            status=MatchParticipantStatus.CONFIRMED,
        )

    def record_score(
        self,
        score: int,
        *,
        is_winner: bool = False,
    ) -> MatchParticipant:
        """Registra o placar contextual do participante."""

        return replace(
            self,
            score=score,
            is_winner=is_winner,
        )

    def change_status(
        self,
        status: MatchParticipantStatus,
    ) -> MatchParticipant:
        """Retorna o participante com novo estado."""

        if not isinstance(status, MatchParticipantStatus):
            raise TypeError("status deve ser MatchParticipantStatus.")

        return replace(self, status=status)
