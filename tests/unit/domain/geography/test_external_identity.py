"""Testes das identidades externas geográficas."""

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from ultrastats_ai.domain.geography import (
    DuplicateExternalIdentityError,
    ExternalIdentityNotFoundError,
    GeographyEntityKind,
    GeographyExternalIdentities,
    GeographyExternalIdentityMapping,
)
from ultrastats_ai.domain.shared import (
    CanonicalId,
    ExternalIdentifier,
    ExternalIdentity,
    ProviderNamespace,
)


def make_entity_id(
    value: str = "00000000-0000-0000-0000-000000001001",
) -> CanonicalId:
    """Cria uma identidade canônica determinística."""
    return CanonicalId(UUID(value))


def make_external_identity(
    *,
    provider: str = "football_data",
    identifier: str = "city-123",
) -> ExternalIdentity:
    """Cria uma identidade externa válida."""
    return ExternalIdentity(
        provider=ProviderNamespace(provider),
        identifier=ExternalIdentifier(identifier),
    )


def make_mapping(
    *,
    entity_id: CanonicalId | None = None,
    entity_kind: GeographyEntityKind = GeographyEntityKind.CITY,
    external_identity: ExternalIdentity | None = None,
) -> GeographyExternalIdentityMapping:
    """Cria um mapeamento externo válido."""
    return GeographyExternalIdentityMapping(
        entity_id=entity_id or make_entity_id(),
        entity_kind=entity_kind,
        external_identity=(
            external_identity
            or make_external_identity()
        ),
    )


def test_mapping_is_created() -> None:
    entity_id = make_entity_id()
    external_identity = make_external_identity()

    mapping = GeographyExternalIdentityMapping(
        entity_id=entity_id,
        entity_kind=GeographyEntityKind.CITY,
        external_identity=external_identity,
    )

    assert mapping.entity_id == entity_id
    assert mapping.entity_kind is GeographyEntityKind.CITY
    assert mapping.external_identity == external_identity
    assert mapping.provider == external_identity.provider
    assert mapping.key == external_identity.key


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_message"),
    [
        ("entity_id", "invalid", "CanonicalId"),
        (
            "entity_kind",
            "city",
            "GeographyEntityKind",
        ),
        (
            "external_identity",
            "football_data:123",
            "ExternalIdentity",
        ),
    ],
)
def test_mapping_rejects_invalid_types(
    field_name: str,
    invalid_value: object,
    expected_message: str,
) -> None:
    values: dict[str, object] = {
        "entity_id": make_entity_id(),
        "entity_kind": GeographyEntityKind.CITY,
        "external_identity": make_external_identity(),
    }

    values[field_name] = invalid_value

    with pytest.raises(TypeError, match=expected_message):
        GeographyExternalIdentityMapping(
            **values  # type: ignore[arg-type]
        )


def test_mapping_belongs_to_entity() -> None:
    entity_id = make_entity_id()
    mapping = make_mapping(entity_id=entity_id)

    assert mapping.belongs_to(entity_id)
    assert mapping.belongs_to(
        entity_id,
        GeographyEntityKind.CITY,
    )


def test_mapping_does_not_belong_to_another_kind() -> None:
    mapping = make_mapping()

    assert not mapping.belongs_to(
        mapping.entity_id,
        GeographyEntityKind.REGION,
    )


def test_mapping_belongs_to_returns_false_for_invalid_types() -> None:
    mapping = make_mapping()

    assert not mapping.belongs_to(  # type: ignore[arg-type]
        "invalid"
    )

    assert not mapping.belongs_to(  # type: ignore[arg-type]
        mapping.entity_id,
        "city",
    )


def test_mapping_is_from_provider() -> None:
    provider = ProviderNamespace("football_data")
    mapping = make_mapping()

    assert mapping.is_from_provider(provider)


def test_mapping_is_from_provider_returns_false_for_invalid_type() -> None:
    mapping = make_mapping()

    assert not mapping.is_from_provider(  # type: ignore[arg-type]
        "football_data"
    )


def test_empty_collection_is_created() -> None:
    identities = GeographyExternalIdentities.empty()

    assert len(identities) == 0
    assert not identities
    assert tuple(identities) == ()


def test_collection_from_iterable() -> None:
    first = make_mapping()

    second = make_mapping(
        entity_id=make_entity_id(
            "00000000-0000-0000-0000-000000001002"
        ),
        external_identity=make_external_identity(
            identifier="city-456"
        ),
    )

    identities = GeographyExternalIdentities.from_iterable(
        [first, second]
    )

    assert len(identities) == 2
    assert tuple(identities) == (first, second)


def test_collection_rejects_non_iterable() -> None:
    with pytest.raises(TypeError, match="iterável"):
        GeographyExternalIdentities.from_iterable(
            10  # type: ignore[arg-type]
        )


def test_collection_rejects_string() -> None:
    with pytest.raises(TypeError, match="iterável"):
        GeographyExternalIdentities.from_iterable(
            "invalid"  # type: ignore[arg-type]
        )


def test_collection_rejects_invalid_item() -> None:
    with pytest.raises(
        TypeError,
        match="GeographyExternalIdentityMapping",
    ):
        GeographyExternalIdentities.from_iterable(
            ["invalid"]  # type: ignore[list-item]
        )


def test_collection_rejects_duplicate_external_identity() -> None:
    external_identity = make_external_identity()

    first = make_mapping(
        external_identity=external_identity
    )

    second = make_mapping(
        entity_id=make_entity_id(
            "00000000-0000-0000-0000-000000001002"
        ),
        entity_kind=GeographyEntityKind.REGION,
        external_identity=external_identity,
    )

    with pytest.raises(DuplicateExternalIdentityError):
        GeographyExternalIdentities.from_iterable(
            [first, second]
        )


def test_add_returns_new_collection() -> None:
    original = GeographyExternalIdentities.empty()
    mapping = make_mapping()

    updated = original.add(mapping)

    assert len(original) == 0
    assert len(updated) == 1
    assert updated.contains(mapping.external_identity)
    assert updated is not original


def test_add_rejects_duplicate_external_identity() -> None:
    mapping = make_mapping()
    identities = GeographyExternalIdentities.from_iterable(
        [mapping]
    )

    with pytest.raises(DuplicateExternalIdentityError):
        identities.add(mapping)


def test_add_rejects_invalid_type() -> None:
    identities = GeographyExternalIdentities.empty()

    with pytest.raises(
        TypeError,
        match="GeographyExternalIdentityMapping",
    ):
        identities.add("invalid")  # type: ignore[arg-type]


def test_discard_returns_new_collection() -> None:
    mapping = make_mapping()

    original = GeographyExternalIdentities.from_iterable(
        [mapping]
    )

    updated = original.discard(
        mapping.external_identity
    )

    assert len(original) == 1
    assert len(updated) == 0
    assert updated is not original


def test_discard_rejects_unknown_identity() -> None:
    identities = GeographyExternalIdentities.empty()

    with pytest.raises(ExternalIdentityNotFoundError):
        identities.discard(make_external_identity())


def test_discard_rejects_invalid_type() -> None:
    identities = GeographyExternalIdentities.empty()

    with pytest.raises(TypeError, match="ExternalIdentity"):
        identities.discard(  # type: ignore[arg-type]
            "invalid"
        )


def test_get_returns_mapping() -> None:
    mapping = make_mapping()

    identities = GeographyExternalIdentities.from_iterable(
        [mapping]
    )

    assert identities.get(
        mapping.external_identity
    ) == mapping


def test_get_returns_none_for_unknown_identity() -> None:
    identities = GeographyExternalIdentities.empty()

    assert identities.get(
        make_external_identity()
    ) is None


def test_get_returns_none_for_invalid_type() -> None:
    identities = GeographyExternalIdentities.empty()

    assert identities.get(  # type: ignore[arg-type]
        "invalid"
    ) is None


def test_find_by_provider() -> None:
    first = make_mapping()

    second = make_mapping(
        entity_id=make_entity_id(
            "00000000-0000-0000-0000-000000001002"
        ),
        external_identity=make_external_identity(
            provider="opta",
            identifier="city-456",
        ),
    )

    identities = GeographyExternalIdentities.from_iterable(
        [first, second]
    )

    result = identities.find_by_provider(
        ProviderNamespace("football_data")
    )

    assert result == (first,)


def test_find_by_provider_rejects_invalid_type() -> None:
    identities = GeographyExternalIdentities.empty()

    with pytest.raises(TypeError, match="ProviderNamespace"):
        identities.find_by_provider(  # type: ignore[arg-type]
            "football_data"
        )


def test_find_by_entity() -> None:
    entity_id = make_entity_id()

    city_mapping = make_mapping(
        entity_id=entity_id,
    )

    region_mapping = make_mapping(
        entity_id=entity_id,
        entity_kind=GeographyEntityKind.REGION,
        external_identity=make_external_identity(
            identifier="region-123"
        ),
    )

    identities = GeographyExternalIdentities.from_iterable(
        [city_mapping, region_mapping]
    )

    result = identities.find_by_entity(
        entity_id,
        GeographyEntityKind.CITY,
    )

    assert result == (city_mapping,)


def test_find_by_entity_without_kind_returns_all_kinds() -> None:
    entity_id = make_entity_id()

    first = make_mapping(
        entity_id=entity_id,
    )

    second = make_mapping(
        entity_id=entity_id,
        entity_kind=GeographyEntityKind.REGION,
        external_identity=make_external_identity(
            identifier="region-123"
        ),
    )

    identities = GeographyExternalIdentities.from_iterable(
        [first, second]
    )

    assert identities.find_by_entity(
        entity_id
    ) == (first, second)


def test_find_by_entity_rejects_invalid_id() -> None:
    identities = GeographyExternalIdentities.empty()

    with pytest.raises(TypeError, match="CanonicalId"):
        identities.find_by_entity(  # type: ignore[arg-type]
            "invalid"
        )


def test_mapping_is_immutable() -> None:
    mapping = make_mapping()

    with pytest.raises(FrozenInstanceError):
        mapping.entity_kind = (  # type: ignore[misc]
            GeographyEntityKind.REGION
        )


def test_collection_is_immutable() -> None:
    identities = GeographyExternalIdentities.empty()

    with pytest.raises(FrozenInstanceError):
        identities._items = ()  # type: ignore[misc]