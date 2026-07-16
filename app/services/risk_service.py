from sqlalchemy.orm import Session

from app.core.risk_profiles import (
    get_risk_profile,
)
from app.repositories import (
    BankrollRepository,
    BankrollTransactionRepository,
)
from app.utils.betting_math import (
    calculate_expected_value,
)
from app.utils.risk_math import (
    apply_stake_cap,
    calculate_fractional_kelly,
    calculate_remaining_daily_exposure,
    calculate_stake_amount,
)


class RiskService:
    """Calcula a stake recomendada para uma aposta."""

    def __init__(self, session: Session) -> None:
        self.bankroll_repository = (
            BankrollRepository(session)
        )

        self.transaction_repository = (
            BankrollTransactionRepository(
                session
            )
        )

    def recommend_stake(
        self,
        bankroll_id: int,
        probability: float,
        odd_value: float,
        profile_code: str,
    ) -> dict:
        bankroll = (
            self.bankroll_repository.find_by_id(
                bankroll_id
            )
        )

        if not bankroll:
            raise ValueError(
                "Banca não encontrada."
            )

        if not bankroll.active:
            raise ValueError(
                "A banca está inativa."
            )

        profile = get_risk_profile(
            profile_code
        )

        expected_value = calculate_expected_value(
            probability=probability,
            odd_value=odd_value,
        )

        if expected_value < profile.minimum_ev:
            return {
                "approved": False,
                "reason": (
                    "EV abaixo do mínimo exigido "
                    f"pelo perfil {profile.name}."
                ),
                "profile": profile.name,
                "expected_value": expected_value,
                "stake_amount": 0.0,
                "stake_percentage": 0.0,
                "stake_units": 0.0,
            }

        balance = float(
            bankroll.current_balance
        )

        fractional_kelly = (
            calculate_fractional_kelly(
                probability=probability,
                odd_value=odd_value,
                kelly_multiplier=(
                    profile.kelly_fraction
                ),
            )
        )

        proposed_stake = calculate_stake_amount(
            bankroll_balance=balance,
            stake_fraction=fractional_kelly,
        )

        capped_stake = apply_stake_cap(
            bankroll_balance=balance,
            proposed_stake=proposed_stake,
            max_stake_percentage=(
                profile.max_stake_percentage
            ),
        )

        daily_exposure = (
            self.transaction_repository
            .get_daily_stake_exposure(
                bankroll_id=bankroll.id
            )
        )

        remaining_exposure = (
            calculate_remaining_daily_exposure(
                bankroll_balance=balance,
                current_daily_exposure=(
                    daily_exposure
                ),
                max_daily_exposure_percentage=(
                    profile
                    .max_daily_exposure_percentage
                ),
            )
        )

        final_stake = min(
            capped_stake,
            remaining_exposure,
            balance,
        )

        if final_stake <= 0:
            return {
                "approved": False,
                "reason": (
                    "Limite diário de exposição "
                    "já atingido."
                ),
                "profile": profile.name,
                "expected_value": expected_value,
                "stake_amount": 0.0,
                "stake_percentage": 0.0,
                "stake_units": 0.0,
            }

        unit_value = (
            balance
            * bankroll.unit_percentage
            / 100
        )

        stake_units = (
            final_stake / unit_value
            if unit_value > 0
            else 0.0
        )

        stake_percentage = (
            final_stake / balance * 100
            if balance > 0
            else 0.0
        )

        return {
            "approved": True,
            "reason": "Stake aprovada.",
            "profile": profile.name,
            "expected_value": expected_value,
            "full_balance": balance,
            "fractional_kelly": (
                fractional_kelly
            ),
            "daily_exposure": daily_exposure,
            "remaining_daily_exposure": (
                remaining_exposure
            ),
            "stake_amount": round(
                final_stake,
                2,
            ),
            "stake_percentage": (
                stake_percentage
            ),
            "stake_units": stake_units,
        }
    
    def get_daily_exposure(
        self,
        bankroll_id: int,
    ) -> float:
        """
        Retorna o valor monetário total
        exposto em apostas no dia atual.
        """

        bankroll = (
            self.bankroll_repository.find_by_id(
                bankroll_id
            )
        )

        if not bankroll:
            raise ValueError(
                "Banca não encontrada."
            )

        return (
            self.transaction_repository
            .get_daily_stake_exposure(
                bankroll_id=bankroll_id
            )
        )