from sqlalchemy.orm import Session

from app.repositories import PerformanceRepository
from app.utils.performance_math import (
    calculate_roi,
    calculate_win_rate,
)


class PerformanceService:
    """
    Calcula e organiza os indicadores
    de desempenho do UltraStats AI.
    """

    def __init__(self, session: Session) -> None:
        self.repository = PerformanceRepository(
            session
        )

    def get_general_summary(self) -> dict:
        data = self.repository.get_general_summary()

        data["roi"] = calculate_roi(
            total_profit=data["total_profit"],
            total_stake=data["total_stake"],
        )

        data["win_rate"] = calculate_win_rate(
            won_bets=data["won_bets"],
            lost_bets=data["lost_bets"],
        )

        return data

    def get_market_performance(
        self,
    ) -> list[dict]:
        rows = (
            self.repository
            .get_performance_by_market()
        )

        for row in rows:
            row["roi"] = calculate_roi(
                total_profit=row["total_profit"],
                total_stake=row["total_stake"],
            )

            row["win_rate"] = calculate_win_rate(
                won_bets=row["won_bets"],
                lost_bets=row["lost_bets"],
            )

        return rows

    def get_competition_performance(
        self,
    ) -> list[dict]:
        rows = (
            self.repository
            .get_performance_by_competition()
        )

        for row in rows:
            row["roi"] = calculate_roi(
                total_profit=row["total_profit"],
                total_stake=row["total_stake"],
            )

            row["win_rate"] = calculate_win_rate(
                won_bets=row["won_bets"],
                lost_bets=row["lost_bets"],
            )

        return rows

    def get_profit_timeline(
        self,
    ) -> list[dict]:
        rows = self.repository.get_profit_timeline()

        accumulated_profit = 0.0

        for row in rows:
            accumulated_profit += row[
                "profit_units"
            ]

            row["accumulated_profit"] = (
                accumulated_profit
            )

        return rows