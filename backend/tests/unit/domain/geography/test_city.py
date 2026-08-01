"""Testes da entidade City."""

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from ultrastats_ai.domain.geography import (
    Aliases,
    City,
    CityNameAliasConflictError,
    Country,
    Region,
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


def make_coordinates() -> Coordinates:
    """Cria coordenadas válidas."""
    return Coordinates(
        latitude=Latitude("-21.7845"),
        longitude=Longitude("-48.1780"),
    )


def make_city(
    *,
    city_id: CanonicalId | None = None,
    region: Region | None = None,
    name: Name | None = None,
    aliases: Aliases | None = None,
    coordinates: Coordinates | None = None,
) -> City:
    """Cria uma City válida."""
    return City(
        id=city_id or make_city_id(),
        region=region or make_region(),
        name=name or Name("Araraquara"),
        aliases=aliases or Aliases.empty(),
        coordinates=coordinates,
    )


def test_city_is_created_with_required_fields() -> None:
    city_id = make_city_id()
    region = make_region()
    name = Name("Araraquara")

    city = City(
        id=city_id,
        region=region,
        name=name,
    )

    assert city.id == city_id
    assert city.region == region
    assert city.name == name
    assert city.aliases == Aliases.empty()
    assert city.coordinates is None


def test_city_accepts_aliases_and_coordinates() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("Morada do Sol"),
            AliasValue("AQA"),
        ]
    )
    coordinates = make_coordinates()

    city = make_city(
        aliases=aliases,
        coordinates=coordinates,
    )

    assert city.aliases == aliases
    assert city.coordinates == coordinates


def test_city_country_is_derived_from_region() -> None:
    country = make_country()
    region = make_region(country=country)
    city = make_city(region=region)

    assert city.country == country
    assert city.country is region.country


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_message"),
    [
        ("id", "invalid-id", "CanonicalId"),
        ("region", "São Paulo", "Region"),
        ("name", "Araraquara", "Name"),
        ("aliases", (), "Aliases"),
        ("coordinates", "invalid", "Coordinates"),
    ],
)
def test_city_rejects_invalid_field_types(
    field_name: str,
    invalid_value: object,
    expected_message: str,
) -> None:
    values: dict[str, object] = {
        "id": make_city_id(),
        "region": make_region(),
        "name": Name("Araraquara"),
        "aliases": Aliases.empty(),
        "coordinates": None,
    }

    values[field_name] = invalid_value

    with pytest.raises(TypeError, match=expected_message):
        City(**values)  # type: ignore[arg-type]


def test_city_rejects_primary_name_repeated_as_alias() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("Araraquara"),
        ]
    )

    with pytest.raises(
        CityNameAliasConflictError,
        match="nome principal",
    ):
        make_city(aliases=aliases)


def test_city_detects_name_alias_conflict_ignoring_case() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("ARARAQUARA"),
        ]
    )

    with pytest.raises(CityNameAliasConflictError):
        make_city(aliases=aliases)


def test_city_detects_name_alias_conflict_after_whitespace_normalization() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("  Morada   do   Sol  "),
        ]
    )

    with pytest.raises(CityNameAliasConflictError):
        make_city(
            name=Name("Morada do Sol"),
            aliases=aliases,
        )


def test_rename_returns_a_new_city() -> None:
    original = make_city()
    new_name = Name("Morada do Sol")

    renamed = original.rename(new_name)

    assert original.name == Name("Araraquara")
    assert renamed.name == new_name
    assert renamed.id == original.id
    assert renamed.region == original.region
    assert renamed.aliases == original.aliases
    assert renamed.coordinates == original.coordinates
    assert renamed is not original


def test_rename_rejects_invalid_name_type() -> None:
    city = make_city()

    with pytest.raises(TypeError, match="Name"):
        city.rename("Araraquara")  # type: ignore[arg-type]


def test_rename_revalidates_alias_conflict() -> None:
    city = make_city(
        aliases=Aliases.from_iterable(
            [
                AliasValue("Morada do Sol"),
            ]
        )
    )

    with pytest.raises(CityNameAliasConflictError):
        city.rename(Name("Morada do Sol"))


def test_change_region_returns_a_new_city() -> None:
    original_region = make_region()

    new_region = make_region(
        region_id=make_region_id(
            "00000000-0000-0000-0000-000000000102"
        ),
        name=Name("Minas Gerais"),
    )

    original = make_city(region=original_region)

    updated = original.change_region(new_region)

    assert original.region == original_region
    assert updated.region == new_region
    assert updated.id == original.id
    assert updated.name == original.name
    assert updated is not original


def test_change_region_updates_derived_country() -> None:
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

    city = make_city(region=brazil_region)

    updated = city.change_region(argentina_region)

    assert city.country == brazil
    assert updated.country == argentina


def test_change_region_rejects_invalid_type() -> None:
    city = make_city()

    with pytest.raises(TypeError, match="Region"):
        city.change_region("São Paulo")  # type: ignore[arg-type]


def test_add_alias_returns_a_new_city() -> None:
    original = make_city()
    alias = AliasValue("Morada do Sol")

    updated = original.add_alias(alias)

    assert len(original.aliases) == 0
    assert updated.has_alias(alias)
    assert updated.id == original.id
    assert updated is not original


def test_add_alias_rejects_primary_name() -> None:
    city = make_city()

    with pytest.raises(CityNameAliasConflictError):
        city.add_alias(AliasValue("ARARAQUARA"))


def test_add_alias_rejects_invalid_type() -> None:
    city = make_city()

    with pytest.raises(TypeError, match="AliasValue"):
        city.add_alias("AQA")  # type: ignore[arg-type]


def test_remove_alias_returns_a_new_city() -> None:
    alias = AliasValue("Morada do Sol")

    original = make_city(
        aliases=Aliases.from_iterable([alias])
    )

    updated = original.remove_alias(alias)

    assert original.has_alias(alias)
    assert not updated.has_alias(alias)
    assert updated.id == original.id
    assert updated is not original


def test_remove_alias_rejects_invalid_type() -> None:
    city = make_city()

    with pytest.raises(TypeError, match="AliasValue"):
        city.remove_alias("AQA")  # type: ignore[arg-type]


def test_has_alias_returns_false_for_invalid_type() -> None:
    city = make_city()

    assert not city.has_alias("AQA")  # type: ignore[arg-type]


def test_update_coordinates_returns_a_new_city() -> None:
    original = make_city()
    coordinates = make_coordinates()

    updated = original.update_coordinates(coordinates)

    assert original.coordinates is None
    assert updated.coordinates == coordinates
    assert updated.id == original.id
    assert updated is not original


def test_update_coordinates_rejects_invalid_type() -> None:
    city = make_city()

    with pytest.raises(TypeError, match="Coordinates"):
        city.update_coordinates(  # type: ignore[arg-type]
            "invalid"
        )


def test_clear_coordinates_returns_city_without_coordinates() -> None:
    original = make_city(
        coordinates=make_coordinates()
    )

    updated = original.clear_coordinates()

    assert original.coordinates is not None
    assert updated.coordinates is None
    assert updated.id == original.id
    assert updated is not original


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

    assert city.belongs_to_region(equivalent_region)


def test_belongs_to_region_returns_false_for_another_region() -> None:
    first_region = make_region()

    second_region = make_region(
        region_id=make_region_id(
            "00000000-0000-0000-0000-000000000102"
        ),
        name=Name("Minas Gerais"),
    )

    city = make_city(region=first_region)

    assert not city.belongs_to_region(second_region)


def test_belongs_to_region_returns_false_for_invalid_type() -> None:
    city = make_city()

    assert not city.belongs_to_region(  # type: ignore[arg-type]
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

    assert city.belongs_to_country(equivalent_country)


def test_belongs_to_country_returns_false_for_another_country() -> None:
    brazil = make_country()

    argentina = make_country(
        country_id=make_country_id(
            "00000000-0000-0000-0000-000000000002"
        ),
        code=CountryCode("ARG"),
        name=Name("Argentina"),
    )

    city = make_city(
        region=make_region(country=brazil)
    )

    assert not city.belongs_to_country(argentina)


def test_belongs_to_country_returns_false_for_invalid_type() -> None:
    city = make_city()

    assert not city.belongs_to_country(  # type: ignore[arg-type]
        "Brasil"
    )


def test_cities_with_same_id_are_equal() -> None:
    city_id = make_city_id()

    first = make_city(
        city_id=city_id,
        name=Name("Araraquara"),
    )

    second = make_city(
        city_id=city_id,
        name=Name("Morada do Sol"),
    )

    assert first == second


def test_cities_with_different_ids_are_not_equal() -> None:
    first = make_city(
        city_id=make_city_id(
            "00000000-0000-0000-0000-000000001001"
        )
    )

    second = make_city(
        city_id=make_city_id(
            "00000000-0000-0000-0000-000000001002"
        )
    )

    assert first != second


def test_city_comparison_with_other_type_is_false() -> None:
    city = make_city()

    assert city != object()


def test_equal_cities_have_equal_hashes() -> None:
    city_id = make_city_id()

    first = make_city(
        city_id=city_id,
        name=Name("Araraquara"),
    )

    second = make_city(
        city_id=city_id,
        name=Name("Morada do Sol"),
    )

    assert hash(first) == hash(second)


def test_city_can_be_used_in_a_set() -> None:
    city_id = make_city_id()

    cities = {
        make_city(
            city_id=city_id,
            name=Name("Araraquara"),
        ),
        make_city(
            city_id=city_id,
            name=Name("Morada do Sol"),
        ),
    }

    assert len(cities) == 1


def test_city_is_immutable() -> None:
    city = make_city()

    with pytest.raises(FrozenInstanceError):
        city.name = Name("Outro nome")  # type: ignore[misc]