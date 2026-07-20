"""Testes do Value Object OrganizationName."""

import pytest

from ultrastats_ai.domain.shared import OrganizationName, ProperName
from ultrastats_ai.domain.shared.names import (
    OrganizationName as NamesPackageOrganizationName,
)
from ultrastats_ai.domain.shared.names.organizations import (
    OrganizationName as OrganizationsPackageOrganizationName,
)


def test_organization_name_inherits_from_proper_name() -> None:
    organization_name = OrganizationName("São Paulo Futebol Clube")

    assert isinstance(organization_name, ProperName)


def test_organization_name_normalizes_whitespace() -> None:
    organization_name = OrganizationName(
        "  Confederação   Brasileira   de   Futebol  "
    )

    assert organization_name.value == "Confederação Brasileira de Futebol"


def test_organization_name_preserves_unicode_characters() -> None:
    organization_name = OrganizationName(
        "Confederação Brasileira de Futebol"
    )

    assert organization_name.value == "Confederação Brasileira de Futebol"


def test_organization_name_accepts_abbreviation() -> None:
    organization_name = OrganizationName("UEFA")

    assert organization_name.value == "UEFA"


def test_organization_name_preserves_legal_suffixes() -> None:
    organization_name = OrganizationName("Red Bull GmbH")

    assert organization_name.value == "Red Bull GmbH"


def test_organization_name_preserves_punctuation() -> None:
    organization_name = OrganizationName("Paris Saint-Germain F.C.")

    assert organization_name.value == "Paris Saint-Germain F.C."


def test_organization_name_equality_uses_value_and_type() -> None:
    first = OrganizationName("FIFA")
    second = OrganizationName("FIFA")

    assert first == second
    assert hash(first) == hash(second)


def test_organization_name_is_immutable() -> None:
    organization_name = OrganizationName("FIFA")

    with pytest.raises((AttributeError, TypeError)):
        organization_name.value = "UEFA"


def test_organization_name_is_distinct_from_other_name_types() -> None:
    from ultrastats_ai.domain.shared import CompetitionName

    organization_name = OrganizationName("Premier League")
    competition_name = CompetitionName("Premier League")

    assert organization_name != competition_name
    assert type(organization_name) is not type(competition_name)


def test_public_apis_export_same_organization_name_class() -> None:
    assert OrganizationName is NamesPackageOrganizationName
    assert (
        OrganizationName
        is OrganizationsPackageOrganizationName
    )