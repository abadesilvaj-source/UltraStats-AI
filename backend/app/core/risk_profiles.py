from dataclasses import dataclass


@dataclass(frozen=True)
class RiskProfile:
    """Configurações de um perfil de gestão de risco."""

    name: str
    kelly_fraction: float
    max_stake_percentage: float
    max_daily_exposure_percentage: float
    minimum_ev: float


RISK_PROFILES = {
    "conservative": RiskProfile(
        name="Conservador",
        kelly_fraction=0.25,
        max_stake_percentage=1.0,
        max_daily_exposure_percentage=3.0,
        minimum_ev=0.03,
    ),
    "moderate": RiskProfile(
        name="Moderado",
        kelly_fraction=0.50,
        max_stake_percentage=2.0,
        max_daily_exposure_percentage=5.0,
        minimum_ev=0.02,
    ),
    "aggressive": RiskProfile(
        name="Agressivo",
        kelly_fraction=0.75,
        max_stake_percentage=3.0,
        max_daily_exposure_percentage=8.0,
        minimum_ev=0.01,
    ),
}


def get_risk_profile(
    profile_code: str,
) -> RiskProfile:
    profile = RISK_PROFILES.get(
        profile_code.lower()
    )

    if not profile:
        valid_profiles = ", ".join(
            RISK_PROFILES.keys()
        )

        raise ValueError(
            f"Perfil de risco inválido. "
            f"Opções: {valid_profiles}."
        )

    return profile