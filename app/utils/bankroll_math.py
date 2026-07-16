def calculate_unit_value(
    bankroll_balance: float,
    unit_percentage: float,
) -> float:
    """Calcula o valor monetário de uma unidade."""

    if bankroll_balance < 0:
        raise ValueError(
            "O saldo não pode ser negativo."
        )

    if unit_percentage <= 0:
        raise ValueError(
            "O percentual deve ser maior que zero."
        )

    if unit_percentage > 100:
        raise ValueError(
            "O percentual não pode ultrapassar 100%."
        )

    return (
        bankroll_balance
        * unit_percentage
        / 100
    )