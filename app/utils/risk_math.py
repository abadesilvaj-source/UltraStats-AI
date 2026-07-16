def calculate_full_kelly_fraction(
    probability: float,
    odd_value: float,
) -> float:
    """
    Calcula a fração integral de Kelly.

    Retorna uma fração entre 0 e 1.

    Exemplo:
    0.05 representa 5% da banca.
    """

    if probability < 0 or probability > 1:
        raise ValueError(
            "A probabilidade deve estar entre 0 e 1."
        )

    if odd_value <= 1:
        raise ValueError(
            "A odd deve ser maior que 1.00."
        )

    net_odd = odd_value - 1
    losing_probability = 1 - probability

    kelly_fraction = (
        (
            net_odd * probability
        )
        - losing_probability
    ) / net_odd

    return max(0.0, kelly_fraction)


def calculate_fractional_kelly(
    probability: float,
    odd_value: float,
    kelly_multiplier: float,
) -> float:
    """
    Aplica uma fração sobre o Kelly integral.

    Exemplo:
    Kelly integral = 10%
    Multiplicador = 0.50
    Resultado = 5%
    """

    if kelly_multiplier <= 0:
        raise ValueError(
            "O multiplicador de Kelly deve ser positivo."
        )

    if kelly_multiplier > 1:
        raise ValueError(
            "O multiplicador de Kelly não pode ultrapassar 1."
        )

    full_kelly = calculate_full_kelly_fraction(
        probability=probability,
        odd_value=odd_value,
    )

    return full_kelly * kelly_multiplier


def calculate_stake_amount(
    bankroll_balance: float,
    stake_fraction: float,
) -> float:
    """Converte uma fração da banca em valor monetário."""

    if bankroll_balance < 0:
        raise ValueError(
            "O saldo não pode ser negativo."
        )

    if stake_fraction < 0:
        raise ValueError(
            "A fração da stake não pode ser negativa."
        )

    return bankroll_balance * stake_fraction


def apply_stake_cap(
    bankroll_balance: float,
    proposed_stake: float,
    max_stake_percentage: float,
) -> float:
    """Aplica o limite máximo por aposta."""

    if max_stake_percentage <= 0:
        raise ValueError(
            "O limite por aposta deve ser positivo."
        )

    maximum_stake = (
        bankroll_balance
        * max_stake_percentage
        / 100
    )

    return min(
        proposed_stake,
        maximum_stake,
    )


def calculate_remaining_daily_exposure(
    bankroll_balance: float,
    current_daily_exposure: float,
    max_daily_exposure_percentage: float,
) -> float:
    """
    Calcula quanto ainda pode ser exposto no dia.
    """

    maximum_daily_exposure = (
        bankroll_balance
        * max_daily_exposure_percentage
        / 100
    )

    remaining = (
        maximum_daily_exposure
        - current_daily_exposure
    )

    return max(0.0, remaining)