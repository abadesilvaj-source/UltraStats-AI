"""Testes da entidade Stadium."""

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from ultrastats_ai.domain.geography import (
    Aliases,
    City,
    Country,
    Region,
    Stadium,
    StadiumNameAliasConflictError,
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


def make_country_id(
    value: str = "00000000-0000-0000-0000-000000000001",
) -> CanonicalId:
    """Cria uma identidade determinística para Country."""
    return CanonicalId(UUID(value))


def make_region_id(
    value: str = "00000000-0000-0000-0000-000000000101",
) -> CanonicalId:
    """Cria uma identidade determinística para Region."""
    return CanonicalId(UUID(value))


def make_city_id(
    value: str = "00000000-0000-0000-0000-000000001001",
) -> CanonicalId:
    """Cria uma identidade determinística para City."""
    return CanonicalId(UUID(value))


def make_stadium_id(
    value: str = "00000000-0000-0000-0000-000000010001",
) -> CanonicalId:
    """Cria uma identidade determinística para Stadium."""
    return CanonicalId(UUID(value))


def make_country(
    *,
    country_id: CanonicalId | None = None,
    code: CountryCode | None = None,
    name: Name | None = None,
) -> Country:
    """Cria um Country válido."""
    return Country(
        id=country_id or make_country_id(),
        code=code or CountryCode("BRA"),
        name=name or Name("Brasil"),
    )


def make_region(
    *,
    region_id: CanonicalId | None = None,
    country: Country | None = None,
    name: Name | None = None,
) -> Region:
    """Cria uma Region válida."""
    return Region(
        id=region_id or make_region_id(),
        country=country or make_country(),
        name=name or Name("São Paulo"),
    )


def make_city(
    *,
    city_id: CanonicalId | None = None,
    region: Region | None = None,
    name: Name | None = None,
) -> City:
    """Cria uma City válida."""
    return City(
        id=city_id or make_city_id(),
        region=region or make_region(),
        name=name or Name("São Paulo"),
    )


def make_coordinates() -> Coordinates:
    """Cria coordenadas válidas."""
    return Coordinates(
        latitude=Latitude("-23.5275"),
        longitude=Longitude("-46.6780"),
    )


def make_stadium(
    *,
    stadium_id: CanonicalId | None = None,
    city: City | None = None,
    name: Name | None = None,
    aliases: Aliases | None = None,
    coordinates: Coordinates | None = None,
) -> Stadium:
    """Cria um Stadium válido."""
    return Stadium(
        id=stadium_id or make_stadium_id(),
        city=city or make_city(),
        name=name or Name("Allianz Parque"),
        aliases=aliases or Aliases.empty(),
        coordinates=coordinates,
    )


def test_stadium_is_created_with_required_fields() -> None:
    stadium_id = make_stadium_id()
    city = make_city()
    name = Name("Allianz Parque")

    stadium = Stadium(
        id=stadium_id,
        city=city,
        name=name,
    )

    assert stadium.id == stadium_id
    assert stadium.city == city
    assert stadium.name == name
    assert stadium.aliases == Aliases.empty()
    assert stadium.coordinates is None


def test_stadium_accepts_aliases_and_coordinates() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("Arena Palmeiras"),
            AliasValue("Arena Palestra"),
        ]
    )
    coordinates = make_coordinates()

    stadium = make_stadium(
        aliases=aliases,
        coordinates=coordinates,
    )

    assert stadium.aliases == aliases
    assert stadium.coordinates == coordinates


def test_stadium_region_is_derived_from_city() -> None:
    region = make_region()
    city = make_city(region=region)
    stadium = make_stadium(city=city)

    assert stadium.region == region
    assert stadium.region is city.region


def test_stadium_country_is_derived_from_city() -> None:
    country = make_country()
    region = make_region(country=country)
    city = make_city(region=region)
    stadium = make_stadium(city=city)

    assert stadium.country == country
    assert stadium.country is city.country


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_message"),
    [
        ("id", "invalid-id", "CanonicalId"),
        ("city", "São Paulo", "City"),
        ("name", "Allianz Parque", "Name"),
        ("aliases", (), "Aliases"),
        ("coordinates", "invalid", "Coordinates"),
    ],
)
def test_stadium_rejects_invalid_field_types(
    field_name: str,
    invalid_value: object,
    expected_message: str,
) -> None:
    values: dict[str, object] = {
        "id": make_stadium_id(),
        "city": make_city(),
        "name": Name("Allianz Parque"),
        "aliases": Aliases.empty(),
        "coordinates": None,
    }

    values[field_name] = invalid_value

    with pytest.raises(TypeError, match=expected_message):
        Stadium(**values)  # type: ignore[arg-type]


def test_stadium_rejects_primary_name_repeated_as_alias() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("Allianz Parque"),
        ]
    )

    with pytest.raises(
        StadiumNameAliasConflictError,
        match="nome principal",
    ):
        make_stadium(aliases=aliases)


def test_stadium_detects_name_alias_conflict_ignoring_case() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("ALLIANZ PARQUE"),
        ]
    )

    with pytest.raises(StadiumNameAliasConflictError):
        make_stadium(aliases=aliases)


def test_stadium_detects_name_alias_conflict_after_whitespace_normalization() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("  Allianz   Parque  "),
        ]
    )

    with pytest.raises(StadiumNameAliasConflictError):
        make_stadium(
            name=Name("Allianz Parque"),
            aliases=aliases,
        )


def test_rename_returns_a_new_stadium() -> None:
    original = make_stadium()
    new_name = Name("Arena Palmeiras")

    renamed = original.rename(new_name)

    assert original.name == Name("Allianz Parque")
    assert renamed.name == new_name
    assert renamed.id == original.id
    assert renamed.city == original.city
    assert renamed.aliases == original.aliases
    assert renamed.coordinates == original.coordinates
    assert renamed is not original


def test_rename_rejects_invalid_name_type() -> None:
    stadium = make_stadium()

    with pytest.raises(TypeError, match="Name"):
        stadium.rename("Arena")  # type: ignore[arg-type]


def test_rename_revalidates_alias_conflict() -> None:
    stadium = make_stadium(
        aliases=Aliases.from_iterable(
            [
                AliasValue("Arena Palmeiras"),
            ]
        )
    )

    with pytest.raises(StadiumNameAliasConflictError):
        stadium.rename(Name("Arena Palmeiras"))


def test_change_city_returns_a_new_stadium() -> None:
    original_city = make_city()

    new_city = make_city(
        city_id=make_city_id(
            "00000000-0000-0000-0000-000000001002"
        ),
        name=Name("Campinas"),
    )

    original = make_stadium(city=original_city)

    updated = original.change_city(new_city)

    assert original.city == original_city
    assert updated.city == new_city
    assert updated.id == original.id
    assert updated.name == original.name
    assert updated is not original


def test_change_city_updates_derived_region() -> None:
    first_region = make_region()

    second_region = make_region(
        region_id=make_region_id(
            "00000000-0000-0000-0000-000000000102"
        ),
        name=Name("Minas Gerais"),
    )

    first_city = make_city(region=first_region)

    second_city = make_city(
        city_id=make_city_id(
            "00000000-0000-0000-0000-000000001002"
        ),
        region=second_region,
        name=Name("Belo Horizonte"),
    )

    stadium = make_stadium(city=first_city)

    updated = stadium.change_city(second_city)

    assert stadium.region == first_region
    assert updated.region == second_region


def test_change_city_updates_derived_country() -> None:
    brazil = make_country()

    argentina = make_country(
        country_id=make_country_id(
            "00000000-0000-0000-0000-000000000002"
        ),
        code=CountryCode("ARG"),
        name=Name("Argentina"),
    )

    brazil_region = make_region(country=brazil)

    argentina_region = make_region(
        region_id=make_region_id(
            "00000000-0000-0000-0000-000000000102"
        ),
        country=argentina,
        name=Name("Buenos Aires"),
    )

    brazil_city = make_city(region=brazil_region)

    argentina_city = make_city(
        city_id=make_city_id(
            "00000000-0000-0000-0000-000000001002"
        ),
        region=argentina_region,
        name=Name("Buenos Aires"),
    )

    stadium = make_stadium(city=brazil_city)

    updated = stadium.change_city(argentina_city)

    assert stadium.country == brazil
    assert updated.country == argentina


def test_change_city_rejects_invalid_type() -> None:
    stadium = make_stadium()

    with pytest.raises(TypeError, match="City"):
        stadium.change_city("São Paulo")  # type: ignore[arg-type]


def test_add_alias_returns_a_new_stadium() -> None:
    original = make_stadium()
    alias = AliasValue("Arena Palmeiras")

    updated = original.add_alias(alias)

    assert len(original.aliases) == 0
    assert updated.has_alias(alias)
    assert updated.id == original.id
    assert updated is not original


def test_add_alias_rejects_primary_name() -> None:
    stadium = make_stadium()

    with pytest.raises(StadiumNameAliasConflictError):
        stadium.add_alias(
            AliasValue("ALLIANZ PARQUE")
        )


def test_add_alias_rejects_invalid_type() -> None:
    stadium = make_stadium()

    with pytest.raises(TypeError, match="AliasValue"):
        stadium.add_alias("Arena")  # type: ignore[arg-type]


def test_remove_alias_returns_a_new_stadium() -> None:
    alias = AliasValue("Arena Palmeiras")

    original = make_stadium(
        aliases=Aliases.from_iterable([alias])
    )

    updated = original.remove_alias(alias)

    assert original.has_alias(alias)
    assert not updated.has_alias(alias)
    assert updated.id == original.id
    assert updated is not original


def test_remove_alias_rejects_invalid_type() -> None:
    stadium = make_stadium()

    with pytest.raises(TypeError, match="AliasValue"):
        stadium.remove_alias("Arena")  # type: ignore[arg-type]


def test_has_alias_returns_false_for_invalid_type() -> None:
    stadium = make_stadium()

    assert not stadium.has_alias(  # type: ignore[arg-type]
        "Arena"
    )


def test_update_coordinates_returns_a_new_stadium() -> None:
    original = make_stadium()
    coordinates = make_coordinates()

    updated = original.update_coordinates(coordinates)

    assert original.coordinates is None
    assert updated.coordinates == coordinates
    assert updated.id == original.id
    assert updated is not original


def test_update_coordinates_rejects_invalid_type() -> None:
    stadium = make_stadium()

    with pytest.raises(TypeError, match="Coordinates"):
        stadium.update_coordinates(  # type: ignore[arg-type]
            "invalid"
        )


def test_clear_coordinates_returns_stadium_without_coordinates() -> None:
    original = make_stadium(
        coordinates=make_coordinates()
    )

    updated = original.clear_coordinates()

    assert original.coordinates is not None
    assert updated.coordinates is None
    assert updated.id == original.id
    assert updated is not original


def test_belongs_to_city_returns_true_for_same_identity() -> None:
    city_id = make_city_id()

    original_city = make_city(
        city_id=city_id,
        name=Name("São Paulo"),
    )

    equivalent_city = make_city(
        city_id=city_id,
        name=Name("Sampa"),
    )

    stadium = make_stadium(city=original_city)

    assert stadium.belongs_to_city(equivalent_city)


def test_belongs_to_city_returns_false_for_another_city() -> None:
    first_city = make_city()

    second_city = make_city(
        city_id=make_city_id(
            "00000000-0000-0000-0000-000000001002"
        ),
        name=Name("Campinas"),
    )

    stadium = make_stadium(city=first_city)

    assert not stadium.belongs_to_city(second_city)


def test_belongs_to_city_returns_false_for_invalid_type() -> None:
    stadium = make_stadium()

    assert not stadium.belongs_to_city(  # type: ignore[arg-type]
        "São Paulo"
    )


def test_belongs_to_region_returns_true_for_same_identity() -> None:
    region_id = make_region_id()

    original_region = make_region(
        region_id=region_id,
        name=Name("São Paulo"),
    )

    equivalent_region = make_region(
        region_id=region_id,
        name=Name("Estado de São Paulo"),
    )

    city = make_city(region=original_region)
    stadium = make_stadium(city=city)

    assert stadium.belongs_to_region(equivalent_region)


def test_belongs_to_region_returns_false_for_another_region() -> None:
    first_region = make_region()

    second_region = make_region(
        region_id=make_region_id(
            "00000000-0000-0000-0000-000000000102"
        ),
        name=Name("Minas Gerais"),
    )

    stadium = make_stadium(
        city=make_city(region=first_region)
    )

    assert not stadium.belongs_to_region(second_region)


def test_belongs_to_region_returns_false_for_invalid_type() -> None:
    stadium = make_stadium()

    assert not stadium.belongs_to_region(  # type: ignore[arg-type]
        "São Paulo"
    )


def test_belongs_to_country_returns_true_for_same_identity() -> None:
    country_id = make_country_id()

    original_country = make_country(
        country_id=country_id,
        name=Name("Brasil"),
    )

    equivalent_country = make_country(
        country_id=country_id,
        name=Name("Brazil"),
    )

    region = make_region(country=original_country)
    city = make_city(region=region)
    stadium = make_stadium(city=city)

    assert stadium.belongs_to_country(equivalent_country)


def test_belongs_to_country_returns_false_for_another_country() -> None:
    brazil = make_country()

    argentina = make_country(
        country_id=make_country_id(
            "00000000-0000-0000-0000-000000000002"
        ),
        code=CountryCode("ARG"),
        name=Name("Argentina"),
    )

    region = make_region(country=brazil)
    city = make_city(region=region)
    stadium = make_stadium(city=city)

    assert not stadium.belongs_to_country(argentina)


def test_belongs_to_country_returns_false_for_invalid_type() -> None:
    stadium = make_stadium()

    assert not stadium.belongs_to_country(  # type: ignore[arg-type]
        "Brasil"
    )


def test_stadiums_with_same_id_are_equal() -> None:
    stadium_id = make_stadium_id()

    first = make_stadium(
        stadium_id=stadium_id,
        name=Name("Allianz Parque"),
    )

    second = make_stadium(
        stadium_id=stadium_id,
        name=Name("Arena Palmeiras"),
    )

    assert first == second


def test_stadiums_with_different_ids_are_not_equal() -> None:
    first = make_stadium(
        stadium_id=make_stadium_id(
            "00000000-0000-0000-0000-000000010001"
        )
    )

    second = make_stadium(
        stadium_id=make_stadium_id(
            "00000000-0000-0000-0000-000000010002"
        )
    )

    assert first != second


def test_stadium_comparison_with_other_type_is_false() -> None:
    stadium = make_stadium()

    assert stadium != object()


def test_equal_stadiums_have_equal_hashes() -> None:
    stadium_id = make_stadium_id()

    first = make_stadium(
        stadium_id=stadium_id,
        name=Name("Allianz Parque"),
    )

    second = make_stadium(
        stadium_id=stadium_id,
        name=Name("Arena Palmeiras"),
    )

    assert hash(first) == hash(second)


def test_stadium_can_be_used_in_a_set() -> None:
    stadium_id = make_stadium_id()

    stadiums = {
        make_stadium(
            stadium_id=stadium_id,
            name=Name("Allianz Parque"),
        ),
        make_stadium(
            stadium_id=stadium_id,
            name=Name("Arena Palmeiras"),
        ),
    }

    assert len(stadiums) == 1


def test_stadium_is_immutable() -> None:
    stadium = make_stadium()

    with pytest.raises(FrozenInstanceError):
        stadium.name = Name("Outro nome")  # type: ignore[misc]