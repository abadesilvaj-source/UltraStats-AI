"""Testes do tipo canônico OrganizationCode."""

import pytest

from ultrastats_ai.domain.shared import OrganizationCode
from ultrastats_ai.domain.shared.codes import (
    OrganizationCode as CodesPackageOrganizationCode,
)
from ultrastats_ai.domain.shared.codes.code_value import CodeValue


def test_organization_code_inherits_from_code_value() -> None:
    code = OrganizationCode("FIFA")

    assert isinstance(code, CodeValue)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("FIFA", "FIFA"),
        ("uefa", "UEFA"),
        (" cbf ", "CBF"),
        ("CONMEBOL", "CONMEBOL"),
        ("SAO_PAULO_FC", "SAO_PAULO_FC"),
        ("ORGANIZATION-001", "ORGANIZATION-001"),
    ],
)
def test_organization_code_accepts_and_normalizes_valid_values(
    value: str,
    expected: str,
) -> None:
    code = OrganizationCode(value)

    assert code.value == expected


@pytest.mark.parametrize(
    "value",
    [
        "SAO PAULO FC",
        "FIFA/UEFA",
        "CONFEDERAÇÃO",
        "CBF#1",
        "",
        "   ",
    ],
)
def test_organization_code_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        OrganizationCode(value)


def test_organization_code_equality_uses_normalized_value() -> None:
    first = OrganizationCode("fifa")
    second = OrganizationCode("FIFA")

    assert first == second
    assert hash(first) == hash(second)


def test_organization_code_is_immutable() -> None:
    code = OrganizationCode("FIFA")

    with pytest.raises((AttributeError, TypeError)):
        code.value = "UEFA"  # type: ignore[misc]


def test_organization_code_public_apis_export_same_class() -> None:
    assert OrganizationCode is CodesPackageOrganizationCode