"""Aggregate Root canônico de uma partida."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from ultrastats_ai.domain.match.enums import (
    MatchType,
    VenueRole,
    VenueStatus,
)
from ultrastats_ai.domain.match.errors import (
    DuplicateMatchParticipantError,
    DuplicateMatchVenueError,
    DuplicateScheduleChangeError,
    InvalidMatchParticipantsError,
    InvalidMatchScheduleError,
    InvalidMatchStatusTransitionError,
    InvalidMatchVenueError,
    MatchParticipantNotFoundError,
    MatchParticipantOwnershipError,
    MatchVenueOwnershipError,
    MultipleCurrentMatchVenuesError,
    ScheduleChangeOwnershipError,
)
from ultrastats_ai.domain.match.lifecycle import can_transition
from ultrastats_ai.domain.match.participant import MatchParticipant
from ultrastats_ai.domain.match.schedule_change import MatchScheduleChange
from ultrastats_ai.domain.match.venue import MatchVenue
from ultrastats_ai.domain.shared import (
    CompetitionId,
    DomainDate,
    MatchId,
    MatchParticipantId,
    MatchScheduleChangeId,
    MatchStatus,
    MatchVenueId,
    ParticipantRole,
    RoundId,
    SeasonId,
    StageId,
    UtcTimestamp,
    VenueId,
)


@dataclass(frozen=True, slots=True, eq=False)
class Match:
    """Controla o núcleo e os participantes de uma partida."""

    id: MatchId
    competition_id: CompetitionId
    season_id: SeasonId
    match_type: MatchType
    status: MatchStatus
    participants: tuple[MatchParticipant, MatchParticipant]
    stage_id: StageId | None = None
    round_id: RoundId | None = None
    scheduled_date: DomainDate | None = None
    scheduled_start_at: UtcTimestamp | None = None
    schedule_changes: tuple[MatchScheduleChange, ...] = ()
    stadium_id: VenueId | None = None
    venues: tuple[MatchVenue, ...] = ()

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Valida identidade, contexto competitivo e composição."""

        if not isinstance(self.id, MatchId):
            raise TypeError("id deve ser MatchId.")
        if not isinstance(self.competition_id, CompetitionId):
            raise TypeError("competition_id deve ser CompetitionId.")
        if not isinstance(self.season_id, SeasonId):
            raise TypeError("season_id deve ser SeasonId.")
        if not isinstance(self.match_type, MatchType):
            raise TypeError("match_type deve ser MatchType.")
        if not isinstance(self.status, MatchStatus):
            raise TypeError("status deve ser MatchStatus.")
        if self.stage_id is not None and not isinstance(
            self.stage_id,
            StageId,
        ):
            raise TypeError("stage_id deve ser StageId ou None.")
        if self.round_id is not None and not isinstance(
            self.round_id,
            RoundId,
        ):
            raise TypeError("round_id deve ser RoundId ou None.")
        if self.scheduled_date is not None and not isinstance(
            self.scheduled_date,
            DomainDate,
        ):
            raise TypeError(
                "scheduled_date deve ser DomainDate ou None."
            )
        if self.scheduled_start_at is not None and not isinstance(
            self.scheduled_start_at,
            UtcTimestamp,
        ):
            raise TypeError(
                "scheduled_start_at deve ser UtcTimestamp ou None."
            )
        if not isinstance(self.participants, tuple):
            raise TypeError("participants deve ser tuple.")
        if not isinstance(self.schedule_changes, tuple):
            raise TypeError("schedule_changes deve ser tuple.")
        if self.stadium_id is not None and not isinstance(
            self.stadium_id,
            VenueId,
        ):
            raise TypeError("stadium_id deve ser VenueId ou None.")
        if not isinstance(self.venues, tuple):
            raise TypeError("venues deve ser tuple.")
        if len(self.participants) != 2:
            raise InvalidMatchParticipantsError(
                "Uma partida deve possuir exatamente dois participantes."
            )
        if any(
            not isinstance(participant, MatchParticipant)
            for participant in self.participants
        ):
            raise TypeError(
                "participants deve conter apenas MatchParticipant."
            )

        self._validate_schedule()
        self._validate_participants()
        self._validate_schedule_changes()
        self._validate_venues()

    def _validate_schedule(self) -> None:
        if (
            self.status is MatchStatus.SCHEDULED
            and self.scheduled_date is None
            and self.scheduled_start_at is None
        ):
            raise InvalidMatchScheduleError(
                "Partida agendada exige data ou horário programado."
            )

    def _validate_participants(self) -> None:
        ids: set[MatchParticipantId] = set()
        teams: set[object] = set()
        roles: set[ParticipantRole] = set()
        orders: set[int] = set()

        for participant in self.participants:
            if participant.match_id != self.id:
                raise MatchParticipantOwnershipError(
                    "O participante pertence a outra partida."
                )
            if participant.id in ids:
                raise DuplicateMatchParticipantError(
                    "A identidade do participante está duplicada."
                )
            if (
                participant.team_id is not None
                and participant.team_id in teams
            ):
                raise DuplicateMatchParticipantError(
                    "Uma equipe não pode ocupar os dois lados."
                )
            if participant.role in roles:
                raise DuplicateMatchParticipantError(
                    "O papel do participante está duplicado."
                )
            if participant.order in orders:
                raise DuplicateMatchParticipantError(
                    "A ordem do participante está duplicada."
                )

            ids.add(participant.id)
            if participant.team_id is not None:
                teams.add(participant.team_id)
            roles.add(participant.role)
            orders.add(participant.order)

        if roles != {ParticipantRole.HOME, ParticipantRole.AWAY}:
            raise InvalidMatchParticipantsError(
                "A fundação exige participantes HOME e AWAY."
            )

    def _validate_schedule_changes(self) -> None:
        known_ids: set[MatchScheduleChangeId] = set()

        for change in self.schedule_changes:
            if not isinstance(change, MatchScheduleChange):
                raise TypeError(
                    "schedule_changes deve conter MatchScheduleChange."
                )
            if change.match_id != self.id:
                raise ScheduleChangeOwnershipError(
                    "A alteração de agenda pertence a outra partida."
                )
            if change.id in known_ids:
                raise DuplicateScheduleChangeError(
                    "A identidade da alteração de agenda está duplicada."
                )
            known_ids.add(change.id)

    def _validate_venues(self) -> None:
        known_ids: set[MatchVenueId] = set()
        current_primary: MatchVenue | None = None

        for venue in self.venues:
            if not isinstance(venue, MatchVenue):
                raise TypeError("venues deve conter MatchVenue.")
            if venue.match_id != self.id:
                raise MatchVenueOwnershipError(
                    "O local pertence a outra partida."
                )
            if venue.id in known_ids:
                raise DuplicateMatchVenueError(
                    "A identidade do local está duplicada."
                )
            if venue.current_primary:
                if current_primary is not None:
                    raise MultipleCurrentMatchVenuesError(
                        "A partida possui mais de um local principal vigente."
                    )
                current_primary = venue
            known_ids.add(venue.id)

        if current_primary is None:
            if self.stadium_id is not None:
                raise InvalidMatchVenueError(
                    "stadium_id exige um local principal vigente."
                )
            return
        if (
            current_primary.stadium_id is not None
            and self.stadium_id != current_primary.stadium_id
        ):
            raise InvalidMatchVenueError(
                "stadium_id diverge do local principal vigente."
            )

    @property
    def home(self) -> MatchParticipant:
        """Retorna o participante mandante."""

        return next(
            participant
            for participant in self.participants
            if participant.role is ParticipantRole.HOME
        )

    @property
    def away(self) -> MatchParticipant:
        """Retorna o participante visitante."""

        return next(
            participant
            for participant in self.participants
            if participant.role is ParticipantRole.AWAY
        )

    @property
    def current_venue(self) -> MatchVenue | None:
        """Retorna o principal local vigente, quando conhecido."""

        return next(
            (
                venue
                for venue in self.venues
                if venue.current_primary
            ),
            None,
        )

    def find_participant(
        self,
        participant_id: MatchParticipantId,
    ) -> MatchParticipant:
        """Localiza um participante interno por identidade."""

        if not isinstance(participant_id, MatchParticipantId):
            raise TypeError(
                "participant_id deve ser MatchParticipantId."
            )

        for participant in self.participants:
            if participant.id == participant_id:
                return participant

        raise MatchParticipantNotFoundError(
            "O participante não pertence à partida."
        )

    def replace_participant(
        self,
        participant: MatchParticipant,
    ) -> Match:
        """Substitui o estado de um participante preservando sua posição."""

        if not isinstance(participant, MatchParticipant):
            raise TypeError(
                "participant deve ser MatchParticipant."
            )
        if participant.match_id != self.id:
            raise MatchParticipantOwnershipError(
                "O participante pertence a outra partida."
            )

        self.find_participant(participant.id)

        return replace(
            self,
            participants=tuple(
                participant
                if current.id == participant.id
                else current
                for current in self.participants
            ),
        )

    def reschedule(
        self,
        *,
        change_id: MatchScheduleChangeId,
        scheduled_date: DomainDate | None,
        scheduled_start_at: UtcTimestamp | None,
        changed_at: UtcTimestamp,
        reason: str,
    ) -> Match:
        """Atualiza a programação preservando a identidade da partida."""

        if scheduled_date is None and scheduled_start_at is None:
            raise InvalidMatchScheduleError(
                "A partida reagendada exige data ou horário."
            )

        change = MatchScheduleChange(
            id=change_id,
            match_id=self.id,
            previous_date=self.scheduled_date,
            previous_start_at=self.scheduled_start_at,
            new_date=scheduled_date,
            new_start_at=scheduled_start_at,
            changed_at=changed_at,
            reason=reason,
        )

        return replace(
            self,
            scheduled_date=scheduled_date,
            scheduled_start_at=scheduled_start_at,
            status=MatchStatus.SCHEDULED,
            schedule_changes=self.schedule_changes + (change,),
        )

    def change_status(self, status: MatchStatus) -> Match:
        """Atualiza o estado quando a transição é permitida."""

        if not isinstance(status, MatchStatus):
            raise TypeError("status deve ser MatchStatus.")
        if not can_transition(self.status, status):
            raise InvalidMatchStatusTransitionError(
                f"Transição inválida: {self.status} -> {status}."
            )

        return replace(self, status=status)

    def assign_venue(
        self,
        venue: MatchVenue,
        *,
        changed_at: UtcTimestamp,
    ) -> Match:
        """Define um local principal e preserva o anterior no histórico."""

        if not isinstance(venue, MatchVenue):
            raise TypeError("venue deve ser MatchVenue.")
        if not isinstance(changed_at, UtcTimestamp):
            raise TypeError("changed_at deve ser UtcTimestamp.")
        if venue.match_id != self.id:
            raise MatchVenueOwnershipError(
                "O local pertence a outra partida."
            )
        if venue.role is not VenueRole.PRIMARY or (
            venue.status is not VenueStatus.CONFIRMED
        ):
            raise InvalidMatchVenueError(
                "O novo local deve ser PRIMARY e CONFIRMED."
            )
        if any(current.id == venue.id for current in self.venues):
            raise DuplicateMatchVenueError(
                "A identidade do local está duplicada."
            )

        updated_venues = tuple(
            current.retire(changed_at)
            if current.current_primary
            else current
            for current in self.venues
        ) + (venue,)

        return replace(
            self,
            stadium_id=venue.stadium_id,
            venues=updated_venues,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Match):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
