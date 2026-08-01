def validate_probability(probability: float) -> None:
    """Valida se uma probabilidade está entre 0 e 1."""

    if probability < 0 or probability > 1:
        raise ValueError(
            "A probabilidade deve estar entre 0 e 1."
        )


def validate_odd(odd_value: float) -> None:
    """Valida uma odd decimal."""

    if odd_value <= 1:
        raise ValueError(
            "A odd deve ser maior que 1.00."
        )


def calculate_implied_probability(
    odd_value: float,
) -> float:
    """
    Calcula a probabilidade implícita de uma odd.

    Exemplo:
    odd 2.00 = 50% = 0.50
    """

    validate_odd(odd_value)

    return 1 / odd_value


def calculate_expected_value(
    probability: float,
    odd_value: float,
) -> float:
    """
    Calcula o valor esperado da aposta.

    Fórmula:
    EV = probabilidade * odd - 1
    """

    validate_probability(probability)
    validate_odd(odd_value)

    return (probability * odd_value) - 1


def calculate_potential_profit(
    odd_value: float,
    stake_units: float,
) -> float:
    """Calcula o lucro potencial de uma aposta vencedora."""

    validate_odd(odd_value)

    if stake_units <= 0:
        raise ValueError(
            "A stake deve ser maior que zero."
        )

    return stake_units * (odd_value - 1)