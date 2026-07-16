def calculate_roi(
    total_profit: float,
    total_stake: float,
) -> float:
    """
    Calcula o ROI percentual.

    Fórmula:

    ROI = lucro total / stake total × 100
    """

    if total_stake <= 0:
        return 0.0

    return (total_profit / total_stake) * 100


def calculate_win_rate(
    won_bets: int,
    lost_bets: int,
) -> float:
    """
    Calcula a taxa de acerto percentual.

    Apostas anuladas não entram no cálculo.
    """

    decided_bets = won_bets + lost_bets

    if decided_bets <= 0:
        return 0.0

    return (won_bets / decided_bets) * 100


def calculate_average(
    total_value: float,
    quantity: int,
) -> float:
    """Calcula uma média simples."""

    if quantity <= 0:
        return 0.0

    return total_value / quantity