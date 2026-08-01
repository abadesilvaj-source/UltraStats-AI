"""Contexto físico e operacional do local de uma partida."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ultrastats_ai.domain.match.enums import (
    SurfaceCondition,
    SurfaceType,
    VenueRole,
    VenueStatus,
    WeatherCondition,
)
from ultrastats_ai.domain.match.errors import InvalidMatchVenueError
from ultrastats_ai.domain.shared import (
    CityId,
    DecimalValue,
    MatchId,
    MatchVenueId,
    Percentage,
    UtcTimestamp,
    VenueId,
)


_CURRENT_STATUSES = frozenset(
    {
        VenueStatus.PLANNED,
        VenueStatus.PROVISIONAL,
        VenueStatus.PENDING_CONFIRMATION,
        VenueStatus.CONFIRMED,
        VenueStatus.ACTIVE,
    }
)
_CONFIRMED_STATUSES = frozenset(
    {
        VenueStatus.CONFIRMED,
        VenueStatus.ACTIVE,
        VenueStatus.COMPLETED,
    }
)


@dataclass(frozen=True, slots=True)
class MatchVenue:
    """Preserva o contexto de um local dentro do agregado Match."""

    id: MatchVenueId
    match_id: MatchId
    role: VenueRole
    status: VenueStatus
    stadium_id: VenueId | None = None
    city_id: CityId | None = None
    surface_type: SurfaceType | None = None
    surface_condition: SurfaceCondition | None = None
    weather_condition: WeatherCondition | None = None
    temperature_celsius: DecimalValue | None = None
    humidity_percent: Percentage | None = None
    wind_speed_kmh: DecimalValue | None = None
    altitude_meters: int | None = None
    capacity: int | None = None
    operational_capacity: int | None = None
    attendance_limit: int | None = None
    attendance: int | None = None
    is_neutral: bool = False
    is_indoor: bool = False
    is_roof_closed: bool = False
    is_closed_doors: bool = False
    is_temporary: bool = False
    is_alternative: bool = False
    is_confirmed: bool = False
    valid_from: UtcTimestamp | None = None
    valid_until: UtcTimestamp | None = None

    def __post_init__(self) -> None:
        self.validate()

    @property
    def current(self) -> bool:
        """Indica que o registro ainda representa uma opção vigente."""

        return (
            self.valid_until is None
            and self.status in _CURRENT_STATUSES
        )

    @property
    def current_primary(self) -> bool:
        """Indica o principal local reconhecido no estado atual."""

        return self.current and self.role is VenueRole.PRIMARY

    def validate(self) -> None:
        """Valida tipos, capacidade, confirmação e período de validade."""

        required_types = (
            ("id", self.id, MatchVenueId),
            ("match_id", self.match_id, MatchId),
            ("role", self.role, VenueRole),
            ("status", self.status, VenueStatus),
        )
        for field_name, value, expected_type in required_types:
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"{field_name} deve ser {expected_type.__name__}."
                )

        optional_types = (
            ("stadium_id", self.stadium_id, VenueId),
            ("city_id", self.city_id, CityId),
            ("surface_type", self.surface_type, SurfaceType),
            (
                "surface_condition",
                self.surface_condition,
                SurfaceCondition,
            ),
            (
                "weather_condition",
                self.weather_condition,
                WeatherCondition,
            ),
            (
                "temperature_celsius",
                self.temperature_celsius,
                DecimalValue,
            ),
            (
                "humidity_percent",
                self.humidity_percent,
                Percentage,
            ),
            (
                "wind_speed_kmh",
                self.wind_speed_kmh,
                DecimalValue,
            ),
            ("valid_from", self.valid_from, UtcTimestamp),
            ("valid_until", self.valid_until, UtcTimestamp),
        )
        for field_name, value, expected_type in optional_types:
            if value is not None and not isinstance(value, expected_type):
                raise TypeError(
                    f"{field_name} deve ser {expected_type.__name__} ou None."
                )

        for field_name in (
            "is_neutral",
            "is_indoor",
            "is_roof_closed",
            "is_closed_doors",
            "is_temporary",
            "is_alternative",
            "is_confirmed",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise TypeError(f"{field_name} deve ser bool.")

        for field_name in (
            "altitude_meters",
            "capacity",
            "operational_capacity",
            "attendance_limit",
            "attendance",
        ):
            value = getattr(self, field_name)
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool)
            ):
                raise TypeError(f"{field_name} deve ser int ou None.")

        self._validate_invariants()

    def _validate_invariants(self) -> None:
        if self.stadium_id is None and self.city_id is None:
            raise InvalidMatchVenueError(
                "O local exige estádio ou cidade."
            )
        for field_name in (
            "capacity",
            "operational_capacity",
            "attendance_limit",
            "attendance",
        ):
            value = getattr(self, field_name)
            if value is not None and value < 0:
                raise InvalidMatchVenueError(
                    f"{field_name} não pode ser negativo."
                )
        if (
            self.wind_speed_kmh is not None
            and self.wind_speed_kmh.value < 0
        ):
            raise InvalidMatchVenueError(
                "wind_speed_kmh não pode ser negativo."
            )
        if (
            self.operational_capacity is not None
            and self.capacity is not None
            and self.operational_capacity > self.capacity
        ):
            raise InvalidMatchVenueError(
                "A capacidade operacional excede a capacidade."
            )
        if (
            self.attendance_limit is not None
            and self.operational_capacity is not None
            and self.attendance_limit > self.operational_capacity
        ):
            raise InvalidMatchVenueError(
                "O limite de público excede a capacidade operacional."
            )
        effective_limit = (
            self.attendance_limit
            if self.attendance_limit is not None
            else self.operational_capacity
        )
        if (
            self.attendance is not None
            and effective_limit is not None
            and self.attendance > effective_limit
        ):
            raise InvalidMatchVenueError(
                "O público excede o limite disponível."
            )
        if self.is_roof_closed and not self.is_indoor:
            raise InvalidMatchVenueError(
                "Teto fechado exige ambiente coberto."
            )
        if self.is_closed_doors and self.attendance not in (None, 0):
            raise InvalidMatchVenueError(
                "Portões fechados não permitem público."
            )
        if self.is_confirmed != (self.status in _CONFIRMED_STATUSES):
            raise InvalidMatchVenueError(
                "Confirmação incompatível com o status do local."
            )
        if (
            self.valid_from is not None
            and self.valid_until is not None
            and self.valid_until.value < self.valid_from.value
        ):
            raise InvalidMatchVenueError(
                "valid_until não pode anteceder valid_from."
            )

    def retire(self, changed_at: UtcTimestamp) -> MatchVenue:
        """Encerra o local vigente após uma mudança."""

        if not isinstance(changed_at, UtcTimestamp):
            raise TypeError("changed_at deve ser UtcTimestamp.")
        return replace(
            self,
            role=VenueRole.ORIGINAL,
            status=VenueStatus.CHANGED,
            is_confirmed=False,
            valid_until=changed_at,
        )
