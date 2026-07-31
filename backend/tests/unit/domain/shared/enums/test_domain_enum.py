"""Testes da classe-base DomainEnum."""

import pytest

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum
from ultrastats_ai.domain.shared.errors import DomainValidationError


class ExampleStatus(DomainEnum):
    """Enum de apoio utilizado exclusivamente nos testes."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


def test_domain_enum_is_also_string_enum() -> None:
    assert isinstance(ExampleStatus.NOT_STARTED, str)


def test_domain_enum_string_representation_uses_value() -> None:
    assert str(ExampleStatus.IN_PROGRESS) == "in_progress"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("not_started", ExampleStatus.NOT_STARTED),
        ("NOT_STARTED", ExampleStatus.NOT_STARTED),
        ("Not Started", ExampleStatus.NOT_STARTED),
        ("not-started", ExampleStatus.NOT_STARTED),
        ("  in progress  ", ExampleStatus.IN_PROGRESS),
        (
            ExampleStatus.FINISHED,
            ExampleStatus.FINISHED,
        ),
    ],
)
def test_domain_enum_parse_accepts_normalized_values(
    value: ExampleStatus | str,
    expected: ExampleStatus,
) -> None:
    assert ExampleStatus.parse(value) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "unknown",
        "cancelled",
    ],
)
def test_domain_enum_parse_rejects_invalid_strings(
    value: str,
) -> None:
    with pytest.raises(DomainValidationError):
        ExampleStatus.parse(value)


def test_domain_enum_parse_rejects_unsupported_type() -> None:
    with pytest.raises(
        TypeError,
        match="deve receber string",
    ):
        ExampleStatus.parse(123)  # type: ignore[arg-type]


def test_domain_enum_returns_values() -> None:
    assert ExampleStatus.values() == (
        "not_started",
        "in_progress",
        "finished",
    )


def test_domain_enum_returns_names() -> None:
    assert ExampleStatus.names() == (
        "NOT_STARTED",
        "IN_PROGRESS",
        "FINISHED",
    )


def test_domain_enum_returns_choices() -> None:
    assert ExampleStatus.choices() == (
        ("not_started", "NOT_STARTED"),
        ("in_progress", "IN_PROGRESS"),
        ("finished", "FINISHED"),
    )


@pytest.mark.parametrize(
    "value",
    [
        "not_started",
        "NOT STARTED",
        ExampleStatus.NOT_STARTED,
    ],
)
def test_domain_enum_has_value_returns_true(
    value: object,
) -> None:
    assert ExampleStatus.has_value(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "unknown",
        123,
        None,
    ],
)
def test_domain_enum_has_value_returns_false(
    value: object,
) -> None:
    assert not ExampleStatus.has_value(value)