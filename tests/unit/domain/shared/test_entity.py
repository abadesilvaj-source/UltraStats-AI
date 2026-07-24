"""Testes da abstração Entity."""

import pytest

from ultrastats_ai.domain.shared.entity import Entity


class ExampleEntity(Entity[int]):
    """Entidade simples utilizada nos testes."""


class OtherEntity(Entity[int]):
    """Segundo tipo de entidade utilizado nos testes."""


def test_entity_exposes_identifier() -> None:
    entity = ExampleEntity(10)

    assert entity.id == 10


def test_entities_with_same_type_and_id_are_equal() -> None:
    first = ExampleEntity(10)
    second = ExampleEntity(10)

    assert first == second


def test_entities_with_different_ids_are_not_equal() -> None:
    first = ExampleEntity(10)
    second = ExampleEntity(20)

    assert first != second


def test_entities_with_different_types_are_not_equal() -> None:
    first = ExampleEntity(10)
    second = OtherEntity(10)

    assert first != second


def test_entity_can_be_used_in_set() -> None:
    first = ExampleEntity(10)
    second = ExampleEntity(10)

    entities = {first, second}

    assert len(entities) == 1


def test_entity_rejects_missing_identifier() -> None:
    with pytest.raises(ValueError, match="não pode ser None"):
        ExampleEntity(None)  # type: ignore[arg-type]


def test_entity_is_equal_to_itself() -> None:
    entity = ExampleEntity(10)

    assert entity == entity


def test_entity_is_not_equal_to_non_entity() -> None:
    assert ExampleEntity(10) != 10


def test_entity_repr_exposes_type_and_identifier() -> None:
    assert repr(ExampleEntity(10)) == "ExampleEntity(id=10)"
