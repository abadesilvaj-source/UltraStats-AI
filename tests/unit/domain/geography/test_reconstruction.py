"""Testes da reconstrução das entidades geográficas."""

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from ultrastats_ai.domain.geography import (
    Aliases,
    City,
    CityReconstruction,
    Country,
    CountryReconstruction,
    Region,
    RegionReconstruction,
    Stadium,
    StadiumReconstruction,
)
from ultrastats_ai.domain.shared import (
    AliasValue,
    CanonicalId,
    Coordinates,
    CountryCode,
    Latitude,
    Longitude,
    Name,
)


def make_id(value: str) -> CanonicalId:
    """Cria uma identidade canônica determinística."""
    return CanonicalId(UUID(value))


def make_coordinates() -> Coordinates:
    """Cria coordenadas geográficas válidas."""
    return Coordinates(
        latitude=Latitude("-23.5505"),
        longitude=Longitude("-46.6333"),
    )


def make_aliases() -> Aliases:
    """Cria aliases válidos."""
    return Aliases.from_iterable(
        [
            AliasValue("Alias principal"),
            AliasValue("Alias alternativo"),
        ]
    )


def make_country() -> Country:
    """Cria um país válido."""
    return Country(
        id=make_id(
            "00000000-0000-0000-0000-000000000001"
        ),
        code=CountryCode("BRA"),
        name=Name("Brasil"),
        aliases=make_aliases(),
        coordinates=make_coordinates(),
    )


def make_region() -> Region:
    """Cria uma região válida."""
    return Region(
        id=make_id(
            "00000000-0000-0000-0000-000000000101"
        ),
        country=make_country(),
        name=Name("São Paulo"),
        aliases=make_aliases(),
        coordinates=make_coordinates(),
    )


def make_city() -> City:
    """Cria uma cidade válida."""
    return City(
        id=make_id(
            "00000000-0000-0000-0000-000000001001"
        ),
        region=make_region(),
        name=Name("São Paulo"),
        aliases=make_aliases(),
        coordinates=make_coordinates(),
    )


def make_stadium() -> Stadium:
    """Cria um estádio válido."""
    return Stadium(
        id=make_id(
            "00000000-0000-0000-0000-000000010001"
        ),
        city=make_city(),
        name=Name("Estádio Municipal"),
        aliases=make_aliases(),
        coordinates=make_coordinates(),
    )


def test_country_reconstruction_restores_entity() -> None:
    original = make_country()

    state = CountryReconstruction.from_entity(original)
    restored = state.restore()

    assert restored == original
    assert restored is not original
    assert restored.id == original.id
    assert restored.code == original.code
    assert restored.name == original.name
    assert restored.aliases == original.aliases
    assert restored.coordinates == original.coordinates


def test_country_reconstruction_does_not_generate_new_id() -> None:
    original = make_country()

    restored = CountryReconstruction.from_entity(
        original
    ).restore()

    assert restored.id is original.id


def test_country_reconstruction_rejects_invalid_entity() -> None:
    with pytest.raises(TypeError, match="Country"):
        CountryReconstruction.from_entity(  # type: ignore[arg-type]
            "Brasil"
        )


def test_region_reconstruction_restores_entity() -> None:
    original = make_region()

    state = RegionReconstruction.from_entity(original)
    restored = state.restore()

    assert restored == original
    assert restored is not original
    assert restored.id == original.id
    assert restored.country == original.country
    assert restored.name == original.name
    assert restored.aliases == original.aliases
    assert restored.coordinates == original.coordinates


def test_region_reconstruction_preserves_country_reference() -> None:
    original = make_region()

    restored = RegionReconstruction.from_entity(
        original
    ).restore()

    assert restored.country is original.country


def test_region_reconstruction_rejects_invalid_entity() -> None:
    with pytest.raises(TypeError, match="Region"):
        RegionReconstruction.from_entity(  # type: ignore[arg-type]
            "São Paulo"
        )


def test_city_reconstruction_restores_entity() -> None:
    original = make_city()

    state = CityReconstruction.from_entity(original)
    restored = state.restore()

    assert restored == original
    assert restored is not original
    assert restored.id == original.id
    assert restored.region == original.region
    assert restored.country == original.country
    assert restored.name == original.name
    assert restored.aliases == original.aliases
    assert restored.coordinates == original.coordinates


def test_city_reconstruction_preserves_region_reference() -> None:
    original = make_city()

    restored = CityReconstruction.from_entity(
        original
    ).restore()

    assert restored.region is original.region


def test_city_reconstruction_rejects_invalid_entity() -> None:
    with pytest.raises(TypeError, match="City"):
        CityReconstruction.from_entity(  # type: ignore[arg-type]
            "São Paulo"
        )


def test_stadium_reconstruction_restores_entity() -> None:
    original = make_stadium()

    state = StadiumReconstruction.from_entity(original)
    restored = state.restore()

    assert restored == original
    assert restored is not original
    assert restored.id == original.id
    assert restored.city == original.city
    assert restored.region == original.region
    assert restored.country == original.country
    assert restored.name == original.name
    assert restored.aliases == original.aliases
    assert restored.coordinates == original.coordinates


def test_stadium_reconstruction_preserves_city_reference() -> None:
    original = make_stadium()

    restored = StadiumReconstruction.from_entity(
        original
    ).restore()

    assert restored.city is original.city


def test_stadium_reconstruction_rejects_invalid_entity() -> None:
    with pytest.raises(TypeError, match="Stadium"):
        StadiumReconstruction.from_entity(  # type: ignore[arg-type]
            "Estádio Municipal"
        )


@pytest.mark.parametrize(
    ("reconstruction_type", "field_name", "invalid_value"),
    [
        (
            CountryReconstruction,
            "id",
            "invalid",
        ),
        (
            CountryReconstruction,
            "code",
            "BRA",
        ),
        (
            CountryReconstruction,
            "name",
            "Brasil",
        ),
        (
            RegionReconstruction,
            "country",
            "Brasil",
        ),
        (
            CityReconstruction,
            "region",
            "São Paulo",
        ),
        (
            StadiumReconstruction,
            "city",
            "São Paulo",
        ),
    ],
)
def test_reconstruction_rejects_invalid_state_types(
    reconstruction_type: type[object],
    field_name: str,
    invalid_value: object,
) -> None:
    country = make_country()
    region = make_region()
    city = make_city()

    values_by_type: dict[type[object], dict[str, object]] = {
        CountryReconstruction: {
            "id": country.id,
            "code": country.code,
            "name": country.name,
            "aliases": country.aliases,
            "coordinates": country.coordinates,
        },
        RegionReconstruction: {
            "id": region.id,
            "country": region.country,
            "name": region.name,
            "aliases": region.aliases,
            "coordinates": region.coordinates,
        },
        CityReconstruction: {
            "id": city.id,
            "region": city.region,
            "name": city.name,
            "aliases": city.aliases,
            "coordinates": city.coordinates,
        },
        StadiumReconstruction: {
            "id": make_stadium().id,
            "city": make_stadium().city,
            "name": make_stadium().name,
            "aliases": make_stadium().aliases,
            "coordinates": make_stadium().coordinates,
        },
    }

    values = values_by_type[reconstruction_type]
    values[field_name] = invalid_value

    with pytest.raises(TypeError):
        reconstruction_type(**values)  # type: ignore[call-arg]


def test_country_reconstruction_is_immutable() -> None:
    state = CountryReconstruction.from_entity(
        make_country()
    )

    with pytest.raises(FrozenInstanceError):
        state.name = Name("Brazil")  # type: ignore[misc]


def test_region_reconstruction_is_immutable() -> None:
    state = RegionReconstruction.from_entity(
        make_region()
    )

    with pytest.raises(FrozenInstanceError):
        state.name = Name("Outro")  # type: ignore[misc]


def test_city_reconstruction_is_immutable() -> None:
    state = CityReconstruction.from_entity(
        make_city()
    )

    with pytest.raises(FrozenInstanceError):
        state.name = Name("Outra")  # type: ignore[misc]


def test_stadium_reconstruction_is_immutable() -> None:
    state = StadiumReconstruction.from_entity(
        make_stadium()
    )

    with pytest.raises(FrozenInstanceError):
        state.name = Name("Outro")  # type: ignore[misc]