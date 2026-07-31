"""Testes da abstração ValueObject."""

from dataclasses import dataclass

import pytest

from ultrastats_ai.domain.shared.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class ExampleCode(ValueObject):
    value: str

    def validate(self) -> None:
        if len(self.value) != 2:
            raise ValueError("O código deve possuir dois caracteres.")


def test_value_objects_with_same_values_are_equal() -> None:
    first = ExampleCode("BR")
    second = ExampleCode("BR")

    assert first == second


def test_value_objects_with_different_values_are_not_equal() -> None:
    first = ExampleCode("BR")
    second = ExampleCode("AR")

    assert first != second


def test_value_object_is_immutable() -> None:
    value_object = ExampleCode("BR")

    with pytest.raises(AttributeError):
        value_object.value = "AR"  # type: ignore[misc]


def test_value_object_executes_validation() -> None:
    with pytest.raises(
        ValueError,
        match="O código deve possuir dois caracteres.",
    ):
        ExampleCode("BRA")