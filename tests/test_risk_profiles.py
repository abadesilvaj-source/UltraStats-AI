import pytest

from app.core.risk_profiles import (
    get_risk_profile,
)


def test_conservative_profile() -> None:
    profile = get_risk_profile(
        "conservative"
    )

    assert profile.name == "Conservador"
    assert profile.kelly_fraction == 0.25
    assert profile.max_stake_percentage == 1.0


def test_moderate_profile() -> None:
    profile = get_risk_profile(
        "moderate"
    )

    assert profile.name == "Moderado"
    assert profile.kelly_fraction == 0.50
    assert profile.max_stake_percentage == 2.0


def test_aggressive_profile() -> None:
    profile = get_risk_profile(
        "aggressive"
    )

    assert profile.name == "Agressivo"
    assert profile.kelly_fraction == 0.75
    assert profile.max_stake_percentage == 3.0


def test_invalid_profile() -> None:
    with pytest.raises(ValueError):
        get_risk_profile(
            "perfil_inexistente"
        )