"""Testes da entidade Country."""

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from ultrastats_ai.domain.geography import (
    Aliases,
    Country,
    CountryNameAliasConflictError,
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
    """Cria uma identidade canônica determinística para os testes."""
    return CanonicalId(UUID(value))


def make_coordinates() -> Coordinates:
    """Cria coordenadas válidas para os testes."""
    return Coordinates(
        latitude=Latitude("-14.2350"),
        longitude=Longitude("-51.9253"),
    )


def make_country(
    *,
    country_id: CanonicalId | None = None,
    code: CountryCode | None = None,
    name: Name | None = None,
    aliases: Aliases | None = None,
    coordinates: Coordinates | None = None,
) -> Country:
    """Cria um Country válido com valores padrão."""
    return Country(
        id=country_id or make_country_id(),
        code=code or CountryCode("BRA"),
        name=name or Name("Brasil"),
        aliases=aliases or Aliases.empty(),
        coordinates=coordinates,
    )


def test_country_is_created_with_required_fields() -> None:
    country_id = make_country_id()
    code = CountryCode("BRA")
    name = Name("Brasil")

    country = Country(
        id=country_id,
        code=code,
        name=name,
    )

    assert country.id == country_id
    assert country.code == code
    assert country.name == name
    assert country.aliases == Aliases.empty()
    assert country.coordinates is None


def test_country_accepts_aliases_and_coordinates() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("Brazil"),
            AliasValue("República Federativa do Brasil"),
        ]
    )
    coordinates = make_coordinates()

    country = make_country(
        aliases=aliases,
        coordinates=coordinates,
    )

    assert country.aliases == aliases
    assert country.coordinates == coordinates


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_message"),
    [
        ("id", "invalid-id", "CanonicalId"),
        ("code", "BR", "CountryCode"),
        ("name", "Brasil", "Name"),
        ("aliases", (), "Aliases"),
        ("coordinates", "invalid", "Coordinates"),
    ],
)
def test_country_rejects_invalid_field_types(
    field_name: str,
    invalid_value: object,
    expected_message: str,
) -> None:
    values: dict[str, object] = {
    "id": make_country_id(),
    "code": CountryCode("BRA"),
    "name": Name("Brasil"),
    "aliases": Aliases.empty(),
    "coordinates": None,
}

    values[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=expected_message,
    ):
        Country(**values)  # type: ignore[arg-type]


def test_country_rejects_primary_name_repeated_as_alias() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("Brasil"),
        ]
    )

    with pytest.raises(
        CountryNameAliasConflictError,
        match="nome principal",
    ):
        make_country(aliases=aliases)


def test_country_detects_name_alias_conflict_ignoring_case() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("BRASIL"),
        ]
    )

    with pytest.raises(CountryNameAliasConflictError):
        make_country(aliases=aliases)


def test_country_detects_name_alias_conflict_after_whitespace_normalization() -> None:
    aliases = Aliases.from_iterable(
        [
            AliasValue("  República   Federativa  do Brasil "),
        ]
    )

    with pytest.raises(CountryNameAliasConflictError):
        make_country(
            name=Name("República Federativa do Brasil"),
            aliases=aliases,
        )


def test_rename_returns_a_new_country() -> None:
    original = make_country()
    new_name = Name("República Federativa do Brasil")

    renamed = original.rename(new_name)

    assert original.name == Name("Brasil")
    assert renamed.name == new_name
    assert renamed.id == original.id
    assert renamed.code == original.code
    assert renamed.aliases == original.aliases
    assert renamed.coordinates == original.coordinates
    assert renamed is not original


def test_rename_rejects_invalid_name_type() -> None:
    country = make_country()

    with pytest.raises(TypeError, match="Name"):
        country.rename("Brasil")  # type: ignore[arg-type]


def test_rename_revalidates_name_alias_conflicts() -> None:
    country = make_country(
        aliases=Aliases.from_iterable(
            [
                AliasValue("Brazil"),
            ]
        )
    )

    with pytest.raises(CountryNameAliasConflictError):
        country.rename(Name("Brazil"))


def test_change_code_returns_a_new_country() -> None:
    original = make_country()
    new_code = CountryCode("ARG")

    updated = original.change_code(new_code)

    assert original.code == CountryCode("BRA")
    assert updated.code == CountryCode("ARG")
    assert updated.code == new_code
    assert updated.id == original.id
    assert updated.name == original.name
    assert updated is not original


def test_change_code_rejects_invalid_type() -> None:
    country = make_country()

    with pytest.raises(TypeError, match="CountryCode"):
        country.change_code("BRA")  # type: ignore[arg-type]


def test_add_alias_returns_a_new_country() -> None:
    original = make_country()
    alias = AliasValue("Brazil")

    updated = original.add_alias(alias)

    assert len(original.aliases) == 0
    assert updated.has_alias(alias)
    assert updated.id == original.id
    assert updated is not original


def test_add_alias_rejects_primary_name() -> None:
    country = make_country()

    with pytest.raises(CountryNameAliasConflictError):
        country.add_alias(AliasValue("BRASIL"))


def test_add_alias_rejects_invalid_type() -> None:
    country = make_country()

    with pytest.raises(TypeError, match="AliasValue"):
        country.add_alias("Brazil")  # type: ignore[arg-type]


def test_remove_alias_returns_a_new_country() -> None:
    alias = AliasValue("Brazil")
    original = make_country(
        aliases=Aliases.from_iterable([alias])
    )

    updated = original.remove_alias(alias)

    assert original.has_alias(alias)
    assert not updated.has_alias(alias)
    assert updated.id == original.id
    assert updated is not original


def test_remove_alias_rejects_invalid_type() -> None:
    country = make_country()

    with pytest.raises(TypeError, match="AliasValue"):
        country.remove_alias("Brazil")  # type: ignore[arg-type]


def test_has_alias_returns_false_for_invalid_type() -> None:
    country = make_country()

    assert not country.has_alias("Brazil")  # type: ignore[arg-type]


def test_update_coordinates_returns_a_new_country() -> None:
    original = make_country()
    coordinates = make_coordinates()

    updated = original.update_coordinates(coordinates)

    assert original.coordinates is None
    assert updated.coordinates == coordinates
    assert updated.id == original.id
    assert updated is not original


def test_update_coordinates_rejects_invalid_type() -> None:
    country = make_country()

    with pytest.raises(TypeError, match="Coordinates"):
        country.update_coordinates(  # type: ignore[arg-type]
            "invalid"
        )


def test_clear_coordinates_returns_country_without_coordinates() -> None:
    original = make_country(
        coordinates=make_coordinates()
    )

    updated = original.clear_coordinates()

    assert original.coordinates is not None
    assert updated.coordinates is None
    assert updated.id == original.id
    assert updated is not original


def test_countries_with_same_id_are_equal() -> None:
    country_id = make_country_id()

    first = make_country(
        country_id=country_id,
        name=Name("Brasil"),
    )

    second = make_country(
        country_id=country_id,
        name=Name("Brazil"),
        code=CountryCode("BRA"),
    )

    assert first == second


def test_countries_with_different_ids_are_not_equal() -> None:
    first = make_country(
        country_id=make_country_id(
            "00000000-0000-0000-0000-000000000001"
        )
    )

    second = make_country(
        country_id=make_country_id(
            "00000000-0000-0000-0000-000000000002"
        )
    )

    assert first != second


def test_country_comparison_with_other_type_is_false() -> None:
    country = make_country()

    assert country != object()


def test_equal_countries_have_equal_hashes() -> None:
    country_id = make_country_id()

    first = make_country(
        country_id=country_id,
        name=Name("Brasil"),
    )

    second = make_country(
        country_id=country_id,
        name=Name("Brazil"),
    )

    assert hash(first) == hash(second)


def test_country_can_be_used_in_a_set() -> None:
    country_id = make_country_id()

    countries = {
        make_country(
            country_id=country_id,
            name=Name("Brasil"),
        ),
        make_country(
            country_id=country_id,
            name=Name("Brazil"),
        ),
    }

    assert len(countries) == 1


def test_country_is_immutable() -> None:
    country = make_country()

    with pytest.raises(FrozenInstanceError):
        country.name = Name("Brazil")  # type: ignore[misc]