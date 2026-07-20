"""Testes da abstração Entity."""

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