"""Testes do contexto de local pertencente ao Match."""

from dataclasses import replace

import pytest

from ultrastats_ai.domain.match import (
    DuplicateMatchVenueError,
    InvalidMatchVenueError,
    MatchVenue,
    MatchVenueOwnershipError,
    MultipleCurrentMatchVenuesError,
    SurfaceCondition,
    SurfaceType,
    VenueRole,
    VenueStatus,
    WeatherCondition,
)
from ultrastats_ai.domain.shared import (
    CityId,
    DecimalValue,
    MatchId,
    MatchVenueId,
    Percentage,
    UtcTimestamp,
    VenueId,
)

from .conftest import make_match


def valid_values(
    *,
    match_id: MatchId | None = None,
    venue_id: MatchVenueId | None = None,
) -> dict[str, object]:
    return {
        "id": venue_id or MatchVenueId.new(),
        "match_id": match_id or MatchId.new(),
        "role": VenueRole.PRIMARY,
        "status": VenueStatus.CONFIRMED,
        "stadium_id": VenueId.new(),
        "city_id": CityId.new(),
        "surface_type": SurfaceType.NATURAL_GRASS,
        "surface_condition": SurfaceCondition.GOOD,
        "weather_condition": WeatherCondition.SUNNY,
        "temperature_celsius": DecimalValue("24.5"),
        "humidity_percent": Percentage("70"),
        "wind_speed_kmh": DecimalValue("8"),
        "altitude_meters": 760,
        "capacity": 50000,
        "operational_capacity": 45000,
        "attendance_limit": 40000,
        "attendance": 35000,
        "is_neutral": False,
        "is_indoor": True,
        "is_roof_closed": True,
        "is_closed_doors": False,
        "is_temporary": False,
        "is_alternative": False,
        "is_confirmed": True,
        "valid_from": UtcTimestamp("2026-07-25T12:00:00Z"),
        "valid_until": None,
    }


def make_venue(
    *,
    match_id: MatchId,
    venue_id: MatchVenueId | None = None,
    stadium_id: VenueId | None = None,
) -> MatchVenue:
    values = valid_values(match_id=match_id, venue_id=venue_id)
    if stadium_id is not None:
        values["stadium_id"] = stadium_id
    return MatchVenue(**values)  # type: ignore[arg-type]


def test_match_venue_preserves_operational_context() -> None:
    venue = MatchVenue(**valid_values())  # type: ignore[arg-type]

    assert venue.current
    assert venue.current_primary
    assert venue.surface_type is SurfaceType.NATURAL_GRASS
    assert venue.attendance == 35000


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    [
        ("id", object(), "MatchVenueId"),
        ("match_id", object(), "MatchId"),
        ("role", object(), "VenueRole"),
        ("status", object(), "VenueStatus"),
        ("stadium_id", object(), "VenueId"),
        ("city_id", object(), "CityId"),
        ("surface_type", object(), "SurfaceType"),
        ("surface_condition", object(), "SurfaceCondition"),
        ("weather_condition", object(), "WeatherCondition"),
        ("temperature_celsius", object(), "DecimalValue"),
        ("humidity_percent", object(), "Percentage"),
        ("wind_speed_kmh", object(), "DecimalValue"),
        ("valid_from", object(), "UtcTimestamp"),
        ("valid_until", object(), "UtcTimestamp"),
    ],
)
def test_match_venue_rejects_invalid_object_types(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    values = valid_values()
    values[field_name] = invalid_value

    with pytest.raises(TypeError, match=message):
        MatchVenue(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field_name",
    [
        "is_neutral",
        "is_indoor",
        "is_roof_closed",
        "is_closed_doors",
        "is_temporary",
        "is_alternative",
        "is_confirmed",
    ],
)
def test_match_venue_requires_boolean_flags(field_name: str) -> None:
    values = valid_values()
    values[field_name] = 1

    with pytest.raises(TypeError, match=field_name):
        MatchVenue(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field_name",
    [
        "altitude_meters",
        "capacity",
        "operational_capacity",
        "attendance_limit",
        "attendance",
    ],
)
@pytest.mark.parametrize("invalid_value", [True, "100"])
def test_match_venue_requires_integer_counts(
    field_name: str,
    invalid_value: object,
) -> None:
    values = valid_values()
    values[field_name] = invalid_value

    with pytest.raises(TypeError, match=field_name):
        MatchVenue(**values)  # type: ignore[arg-type]


def test_match_venue_requires_stadium_or_city() -> None:
    values = valid_values()
    values["stadium_id"] = None
    values["city_id"] = None

    with pytest.raises(InvalidMatchVenueError, match="estádio ou cidade"):
        MatchVenue(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field_name",
    ["capacity", "operational_capacity", "attendance_limit", "attendance"],
)
def test_match_venue_rejects_negative_counts(field_name: str) -> None:
    values = valid_values()
    values[field_name] = -1

    with pytest.raises(InvalidMatchVenueError, match=field_name):
        MatchVenue(**values)  # type: ignore[arg-type]


def test_match_venue_rejects_negative_wind_speed() -> None:
    values = valid_values()
    values["wind_speed_kmh"] = DecimalValue("-1")

    with pytest.raises(InvalidMatchVenueError, match="wind_speed"):
        MatchVenue(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("operational_capacity", 50001, "operacional"),
        ("attendance_limit", 45001, "limite"),
        ("attendance", 40001, "público"),
    ],
)
def test_match_venue_enforces_capacity_hierarchy(
    field_name: str,
    value: int,
    message: str,
) -> None:
    values = valid_values()
    values[field_name] = value

    with pytest.raises(InvalidMatchVenueError, match=message):
        MatchVenue(**values)  # type: ignore[arg-type]


def test_attendance_uses_operational_capacity_without_specific_limit() -> None:
    values = valid_values()
    values["attendance_limit"] = None
    values["attendance"] = 45001

    with pytest.raises(InvalidMatchVenueError, match="público"):
        MatchVenue(**values)  # type: ignore[arg-type]


def test_closed_roof_requires_indoor_venue() -> None:
    values = valid_values()
    values["is_indoor"] = False

    with pytest.raises(InvalidMatchVenueError, match="Teto fechado"):
        MatchVenue(**values)  # type: ignore[arg-type]


def test_closed_doors_rejects_attendance() -> None:
    values = valid_values()
    values["is_closed_doors"] = True

    with pytest.raises(InvalidMatchVenueError, match="Portões fechados"):
        MatchVenue(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("status", "is_confirmed"),
    [
        (VenueStatus.PLANNED, True),
        (VenueStatus.CONFIRMED, False),
    ],
)
def test_confirmation_must_match_status(
    status: VenueStatus,
    is_confirmed: bool,
) -> None:
    values = valid_values()
    values["status"] = status
    values["is_confirmed"] = is_confirmed

    with pytest.raises(InvalidMatchVenueError, match="Confirmação"):
        MatchVenue(**values)  # type: ignore[arg-type]


def test_validity_period_must_be_ordered() -> None:
    values = valid_values()
    values["valid_until"] = UtcTimestamp("2026-07-24T12:00:00Z")

    with pytest.raises(InvalidMatchVenueError, match="valid_until"):
        MatchVenue(**values)  # type: ignore[arg-type]


def test_non_current_and_non_primary_properties() -> None:
    values = valid_values()
    values.update(
        role=VenueRole.ALTERNATIVE,
        status=VenueStatus.CHANGED,
        is_confirmed=False,
        valid_until=UtcTimestamp("2026-07-26T12:00:00Z"),
    )
    venue = MatchVenue(**values)  # type: ignore[arg-type]

    assert not venue.current
    assert not venue.current_primary


def test_retire_closes_current_venue() -> None:
    venue = MatchVenue(**valid_values())  # type: ignore[arg-type]
    changed_at = UtcTimestamp("2026-07-26T12:00:00Z")

    retired = venue.retire(changed_at)

    assert retired.role is VenueRole.ORIGINAL
    assert retired.status is VenueStatus.CHANGED
    assert retired.valid_until == changed_at
    assert not retired.is_confirmed


def test_retire_rejects_invalid_timestamp() -> None:
    venue = MatchVenue(**valid_values())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="changed_at"):
        venue.retire(object())  # type: ignore[arg-type]


def test_match_rejects_invalid_venue_collection() -> None:
    match = make_match()

    with pytest.raises(TypeError, match="venues deve ser tuple"):
        replace(match, venues=[])  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="MatchVenue"):
        replace(match, venues=(object(),))  # type: ignore[arg-type]


def test_match_rejects_invalid_stadium_identifier() -> None:
    match = make_match()

    with pytest.raises(TypeError, match="stadium_id"):
        replace(match, stadium_id=object())  # type: ignore[arg-type]


def test_match_rejects_venue_from_another_match() -> None:
    match = make_match()

    with pytest.raises(MatchVenueOwnershipError):
        replace(match, venues=(make_venue(match_id=MatchId.new()),))


def test_match_rejects_duplicate_venue_identity() -> None:
    match = make_match()
    venue_id = MatchVenueId.new()
    first = make_venue(match_id=match.id, venue_id=venue_id)
    second = replace(
        first,
        role=VenueRole.ALTERNATIVE,
        status=VenueStatus.PLANNED,
        is_confirmed=False,
    )

    with pytest.raises(DuplicateMatchVenueError):
        replace(
            match,
            stadium_id=first.stadium_id,
            venues=(first, second),
        )


def test_match_rejects_multiple_current_primary_venues() -> None:
    match = make_match()
    first = make_venue(match_id=match.id)
    second = make_venue(match_id=match.id)

    with pytest.raises(MultipleCurrentMatchVenuesError):
        replace(
            match,
            stadium_id=first.stadium_id,
            venues=(first, second),
        )


def test_match_requires_current_venue_for_stadium_reference() -> None:
    match = make_match()

    with pytest.raises(InvalidMatchVenueError, match="local principal"):
        replace(match, stadium_id=VenueId.new())


def test_match_requires_stadium_compatibility() -> None:
    match = make_match()
    venue = make_venue(match_id=match.id)

    with pytest.raises(InvalidMatchVenueError, match="diverge"):
        replace(
            match,
            stadium_id=VenueId.new(),
            venues=(venue,),
        )


def test_assign_venue_preserves_previous_location() -> None:
    match = make_match()
    first = make_venue(match_id=match.id)
    assigned = match.assign_venue(
        first,
        changed_at=UtcTimestamp("2026-07-25T12:00:00Z"),
    )
    second = make_venue(match_id=match.id)

    updated = assigned.assign_venue(
        second,
        changed_at=UtcTimestamp("2026-07-26T12:00:00Z"),
    )

    assert updated.current_venue == second
    assert updated.stadium_id == second.stadium_id
    assert len(updated.venues) == 2
    assert updated.venues[0].status is VenueStatus.CHANGED


def test_assign_venue_validates_command() -> None:
    match = make_match()
    valid = make_venue(match_id=match.id)

    with pytest.raises(TypeError, match="venue"):
        match.assign_venue(  # type: ignore[arg-type]
            object(),
            changed_at=UtcTimestamp("2026-07-25T12:00:00Z"),
        )
    with pytest.raises(TypeError, match="changed_at"):
        match.assign_venue(valid, changed_at=object())  # type: ignore[arg-type]
    with pytest.raises(MatchVenueOwnershipError):
        match.assign_venue(
            make_venue(match_id=MatchId.new()),
            changed_at=UtcTimestamp("2026-07-25T12:00:00Z"),
        )


def test_assign_venue_requires_confirmed_primary_and_unique_identity() -> None:
    match = make_match()
    valid = make_venue(match_id=match.id)
    invalid = replace(
        valid,
        role=VenueRole.ALTERNATIVE,
        status=VenueStatus.PLANNED,
        is_confirmed=False,
    )

    with pytest.raises(InvalidMatchVenueError, match="PRIMARY"):
        match.assign_venue(
            invalid,
            changed_at=UtcTimestamp("2026-07-25T12:00:00Z"),
        )

    assigned = match.assign_venue(
        valid,
        changed_at=UtcTimestamp("2026-07-25T12:00:00Z"),
    )
    with pytest.raises(DuplicateMatchVenueError):
        assigned.assign_venue(
            valid,
            changed_at=UtcTimestamp("2026-07-26T12:00:00Z"),
        )
