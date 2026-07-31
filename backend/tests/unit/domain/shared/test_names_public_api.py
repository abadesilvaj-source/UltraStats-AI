"""Testes da API pública consolidada da biblioteca de nomes."""

from ultrastats_ai.domain.shared import (
    CityName as PublicCityName,
)
from ultrastats_ai.domain.shared import (
    CountryName as PublicCountryName,
)
from ultrastats_ai.domain.shared import (
    DisplayName as PublicDisplayName,
)
from ultrastats_ai.domain.shared import (
    Name as PublicName,
)
from ultrastats_ai.domain.shared import (
    ProperName as PublicProperName,
)
from ultrastats_ai.domain.shared import (
    RegionName as PublicRegionName,
)
from ultrastats_ai.domain.shared import (
    ShortName as PublicShortName,
)
from ultrastats_ai.domain.shared.city_name import (
    CityName as CompatibilityCityName,
)
from ultrastats_ai.domain.shared.country_name import (
    CountryName as CompatibilityCountryName,
)
from ultrastats_ai.domain.shared.display_name import (
    DisplayName as CompatibilityDisplayName,
)
from ultrastats_ai.domain.shared.name import (
    Name as CompatibilityName,
)
from ultrastats_ai.domain.shared.names import (
    CityName,
    CountryName,
    DisplayName,
    Name,
    ProperName,
    RegionName,
    ShortName,
)
from ultrastats_ai.domain.shared.names.base import (
    ProperName as BaseProperName,
)
from ultrastats_ai.domain.shared.names.geography import (
    RegionName as GeographyRegionName,
)
from ultrastats_ai.domain.shared.proper_name import (
    ProperName as CompatibilityProperName,
)
from ultrastats_ai.domain.shared.region_name import (
    RegionName as CompatibilityRegionName,
)
from ultrastats_ai.domain.shared.short_name import (
    ShortName as CompatibilityShortName,
)


def test_public_api_exports_canonical_base_name_types() -> None:
    assert PublicName is Name
    assert PublicProperName is ProperName
    assert PublicDisplayName is DisplayName
    assert PublicShortName is ShortName


def test_public_api_exports_canonical_geography_name_types() -> None:
    assert PublicCountryName is CountryName
    assert PublicRegionName is RegionName
    assert PublicCityName is CityName


def test_compatibility_modules_export_canonical_base_types() -> None:
    assert CompatibilityName is Name
    assert CompatibilityProperName is ProperName
    assert CompatibilityDisplayName is DisplayName
    assert CompatibilityShortName is ShortName


def test_compatibility_modules_export_canonical_geography_types() -> None:
    assert CompatibilityCountryName is CountryName
    assert CompatibilityRegionName is RegionName
    assert CompatibilityCityName is CityName


def test_subpackages_export_same_canonical_types() -> None:
    assert BaseProperName is ProperName
    assert GeographyRegionName is RegionName


def test_objects_created_from_different_import_paths_are_equal() -> None:
    public_name = PublicCountryName("Brazil")
    compatibility_name = CompatibilityCountryName("Brazil")
    package_name = CountryName("Brazil")

    assert public_name == compatibility_name
    assert public_name == package_name
    assert compatibility_name == package_name


def test_objects_created_from_different_import_paths_share_type() -> None:
    public_name = PublicCountryName("Brazil")
    compatibility_name = CompatibilityCountryName("Brazil")
    package_name = CountryName("Brazil")

    assert type(public_name) is type(compatibility_name)
    assert type(public_name) is type(package_name)