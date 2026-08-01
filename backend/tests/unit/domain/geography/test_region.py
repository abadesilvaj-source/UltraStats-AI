"""Testes da entidade Region."""

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from ultrastats_ai.domain.geography import (
    Aliases,
    Country,
    Region,
    RegionNameAliasConflictError,
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


def make_country(
    *,
    country_id: CanonicalId | None = None,
    code: CountryCode | None = None,
    name: Name | None = None,
) -> Country:
    """Cria um Country válido para os testes."""
    return Country(
        id=country_id or make_country_id(),
        code=code or CountryCode("BRA"),
        name=name or Name("Brasil"),
    )


def make_coordinates() -> Coordinates:
    """Cria coordenadas válidas para os testes."""
    return Coordinates(
        latitude=Latitude("-23.5505"),
        longitude=Longitude("-46.6333"),
    )


def make_region(
    *,
    region_id: CanonicalId | None = None,
    country: Country | None = None,
    name: Name | None = None,
    aliases: Aliases | None = None,
    coordinates: Coordinates | None = None,
) -> Region:
    """Cria uma Region válida com valores padrão."""
    return Region(
        id=region_id or make_region_id(),
        country=country or make_country(),
        name=name or Name("São Paulo"),
        aliases=aliases or Aliases.empty(),
        coordinates=coordinates,
    )


def test_region_is_created_with_required_fields() -> None:
    region_id = make_region_id()
    country = make_country()
    name = Name("São Paulo")

    region = Region(
        id=region_id,
        country=country,
        name=name,
    )

    assert region.id == region_id
    assert region.country == country
    assert region.name == name
    assert region.aliases == Aliases.empty()
    assert region.coordinates is None


def test_region_accepts_aliases_and_coordinates() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("Estado de São Paulo"),
            AliasValue("SP"),
        ]
    )
    coordinates = make_coordinates()

    region = make_region(
        aliases=aliases,
        coordinates=coordinates,
    )

    assert region.aliases == aliases
    assert region.coordinates == coordinates


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_message"),
    [
        ("id", "invalid-id", "CanonicalId"),
        ("country", "Brasil", "Country"),
        ("name", "São Paulo", "Name"),
        ("aliases", (), "Aliases"),
        ("coordinates", "invalid", "Coordinates"),
    ],
)
def test_region_rejects_invalid_field_types(
    field_name: str,
    invalid_value: object,
    expected_message: str,
) -> None:
    values: dict[str, object] = {
        "id": make_region_id(),
        "country": make_country(),
        "name": Name("São Paulo"),
        "aliases": Aliases.empty(),
        "coordinates": None,
    }

    values[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=expected_message,
    ):
        Region(**values)  # type: ignore[arg-type]


def test_region_rejects_primary_name_repeated_as_alias() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("São Paulo"),
        ]
    )

    with pytest.raises(
        RegionNameAliasConflictError,
        match="nome principal",
    ):
        make_region(aliases=aliases)


def test_region_detects_name_alias_conflict_ignoring_case() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("SÃO PAULO"),
        ]
    )

    with pytest.raises(RegionNameAliasConflictError):
        make_region(aliases=aliases)


def test_region_detects_name_alias_conflict_after_whitespace_normalization() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("  Estado   de   São Paulo  "),
        ]
    )

    with pytest.raises(RegionNameAliasConflictError):
        make_region(
            name=Name("Estado de São Paulo"),
            aliases=aliases,
        )


def test_rename_returns_a_new_region() -> None:
    original = make_region()
    new_name = Name("Estado de São Paulo")

    renamed = original.rename(new_name)

    assert original.name == Name("São Paulo")
    assert renamed.name == new_name
    assert renamed.id == original.id
    assert renamed.country == original.country
    assert renamed.aliases == original.aliases
    assert renamed.coordinates == original.coordinates
    assert renamed is not original


def test_rename_rejects_invalid_name_type() -> None:
    region = make_region()

    with pytest.raises(TypeError, match="Name"):
        region.rename("São Paulo")  # type: ignore[arg-type]


def test_rename_revalidates_name_alias_conflicts() -> None:
    region = make_region(
        aliases=Aliases.from_iterable(
            [
                AliasValue("Estado de São Paulo"),
            ]
        )
    )

    with pytest.raises(RegionNameAliasConflictError):
        region.rename(Name("Estado de São Paulo"))


def test_change_country_returns_a_new_region() -> None:
    original_country = make_country()
    new_country = make_country(
        country_id=make_country_id(
            "00000000-0000-0000-0000-000000000002"
        ),
        code=CountryCode("ARG"),
        name=Name("Argentina"),
    )
    original = make_region(country=original_country)

    updated = original.change_country(new_country)

    assert original.country == original_country
    assert updated.country == new_country
    assert updated.id == original.id
    assert updated.name == original.name
    assert updated is not original


def test_change_country_rejects_invalid_type() -> None:
    region = make_region()

    with pytest.raises(TypeError, match="Country"):
        region.change_country("Brasil")  # type: ignore[arg-type]


def test_add_alias_returns_a_new_region() -> None:
    original = make_region()
    alias = AliasValue("Estado de São Paulo")

    updated = original.add_alias(alias)

    assert len(original.aliases) == 0
    assert updated.has_alias(alias)
    assert updated.id == original.id
    assert updated is not original


def test_add_alias_rejects_primary_name() -> None:
    region = make_region()

    with pytest.raises(RegionNameAliasConflictError):
        region.add_alias(AliasValue("SÃO PAULO"))


def test_add_alias_rejects_invalid_type() -> None:
    region = make_region()

    with pytest.raises(TypeError, match="AliasValue"):
        region.add_alias("SP")  # type: ignore[arg-type]


def test_remove_alias_returns_a_new_region() -> None:
    alias = AliasValue("Estado de São Paulo")
    original = make_region(
        aliases=Aliases.from_iterable([alias])
    )

    updated = original.remove_alias(alias)

    assert original.has_alias(alias)
    assert not updated.has_alias(alias)
    assert updated.id == original.id
    assert updated is not original


def test_remove_alias_rejects_invalid_type() -> None:
    region = make_region()

    with pytest.raises(TypeError, match="AliasValue"):
        region.remove_alias("SP")  # type: ignore[arg-type]


def test_has_alias_returns_false_for_invalid_type() -> None:
    region = make_region()

    assert not region.has_alias("SP")  # type: ignore[arg-type]


def test_update_coordinates_returns_a_new_region() -> None:
    original = make_region()
    coordinates = make_coordinates()

    updated = original.update_coordinates(coordinates)

    assert original.coordinates is None
    assert updated.coordinates == coordinates
    assert updated.id == original.id
    assert updated is not original


def test_update_coordinates_rejects_invalid_type() -> None:
    region = make_region()

    with pytest.raises(TypeError, match="Coordinates"):
        region.update_coordinates(  # type: ignore[arg-type]
            "invalid"
        )


def test_clear_coordinates_returns_region_without_coordinates() -> None:
    original = make_region(
        coordinates=make_coordinates()
    )

    updated = original.clear_coordinates()

    assert original.coordinates is not None
    assert updated.coordinates is None
    assert updated.id == original.id
    assert updated is not original


def test_belongs_to_returns_true_for_same_country_identity() -> None:
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

    assert region.belongs_to(equivalent_country)


def test_belongs_to_returns_false_for_another_country() -> None:
    brazil = make_country()

    argentina = make_country(
        country_id=make_country_id(
            "00000000-0000-0000-0000-000000000002"
        ),
        code=CountryCode("ARG"),
        name=Name("Argentina"),
    )

    region = make_region(country=brazil)

    assert not region.belongs_to(argentina)


def test_belongs_to_returns_false_for_invalid_type() -> None:
    region = make_region()

    assert not region.belongs_to("Brasil")  # type: ignore[arg-type]


def test_regions_with_same_id_are_equal() -> None:
    region_id = make_region_id()

    first = make_region(
        region_id=region_id,
        name=Name("São Paulo"),
    )

    second = make_region(
        region_id=region_id,
        name=Name("Estado de São Paulo"),
    )

    assert first == second


def test_regions_with_different_ids_are_not_equal() -> None:
    first = make_region(
        region_id=make_region_id(
            "00000000-0000-0000-0000-000000000101"
        )
    )

    second = make_region(
        region_id=make_region_id(
            "00000000-0000-0000-0000-000000000102"
        )
    )

    assert first != second


def test_region_comparison_with_other_type_is_false() -> None:
    region = make_region()

    assert region != object()


def test_equal_regions_have_equal_hashes() -> None:
    region_id = make_region_id()

    first = make_region(
        region_id=region_id,
        name=Name("São Paulo"),
    )

    second = make_region(
        region_id=region_id,
        name=Name("Estado de São Paulo"),
    )

    assert hash(first) == hash(second)


def test_region_can_be_used_in_a_set() -> None:
    region_id = make_region_id()

    regions = {
        make_region(
            region_id=region_id,
            name=Name("São Paulo"),
        ),
        make_region(
            region_id=region_id,
            name=Name("Estado de São Paulo"),
        ),
    }

    assert len(regions) == 1


def test_region_is_immutable() -> None:
    region = make_region()

    with pytest.raises(FrozenInstanceError):
        region.name = Name("Outro nome")  # type: ignore[misc]