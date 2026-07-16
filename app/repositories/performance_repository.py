from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import (
    Bet,
    Competition,
    Market,
    Match,
    Prediction,
)


class PerformanceRepository:
    """
    Realiza consultas agregadas para
    o painel de desempenho.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_general_summary(self) -> dict:
        """
        Retorna os indicadores gerais
        das apostas oficiais liquidadas.
        """

        statement = (
            select(
                func.count(Bet.id).label("total_bets"),

                func.sum(
                    case(
                        (Bet.result == "won", 1),
                        else_=0,
                    )
                ).label("won_bets"),

                func.sum(
                    case(
                        (Bet.result == "lost", 1),
                        else_=0,
                    )
                ).label("lost_bets"),

                func.sum(
                    case(
                        (Bet.result == "void", 1),
                        else_=0,
                    )
                ).label("void_bets"),

                func.coalesce(
                    func.sum(Bet.stake_units),
                    0.0,
                ).label("total_stake"),

                func.coalesce(
                    func.sum(Bet.profit_units),
                    0.0,
                ).label("total_profit"),

                func.avg(Bet.odd_value).label(
                    "average_odd"
                ),

                func.avg(
                    Prediction.expected_value
                ).label("average_ev"),
            )
            .outerjoin(
                Prediction,
                Bet.prediction_id == Prediction.id,
            )
            .where(
                Bet.is_official.is_(True),
                Bet.status == "settled",
            )
        )

        row = self.session.execute(
            statement
        ).one()

        return {
            "total_bets": int(row.total_bets or 0),
            "won_bets": int(row.won_bets or 0),
            "lost_bets": int(row.lost_bets or 0),
            "void_bets": int(row.void_bets or 0),
            "total_stake": float(
                row.total_stake or 0
            ),
            "total_profit": float(
                row.total_profit or 0
            ),
            "average_odd": float(
                row.average_odd or 0
            ),
            "average_ev": float(
                row.average_ev or 0
            ),
        }

    def get_performance_by_market(
        self,
    ) -> list[dict]:
        """
        Agrupa o desempenho por mercado.
        """

        statement = (
            select(
                Market.code.label("market_code"),
                Market.name.label("market_name"),

                func.count(Bet.id).label(
                    "total_bets"
                ),

                func.sum(
                    case(
                        (Bet.result == "won", 1),
                        else_=0,
                    )
                ).label("won_bets"),

                func.sum(
                    case(
                        (Bet.result == "lost", 1),
                        else_=0,
                    )
                ).label("lost_bets"),

                func.coalesce(
                    func.sum(Bet.stake_units),
                    0.0,
                ).label("total_stake"),

                func.coalesce(
                    func.sum(Bet.profit_units),
                    0.0,
                ).label("total_profit"),

                func.avg(Bet.odd_value).label(
                    "average_odd"
                ),
            )
            .join(
                Bet,
                Bet.market_id == Market.id,
            )
            .where(
                Bet.is_official.is_(True),
                Bet.status == "settled",
            )
            .group_by(
                Market.id,
                Market.code,
                Market.name,
            )
            .order_by(
                Market.name
            )
        )

        rows = self.session.execute(
            statement
        ).all()

        return [
            {
                "market_code": row.market_code,
                "market_name": row.market_name,
                "total_bets": int(
                    row.total_bets or 0
                ),
                "won_bets": int(
                    row.won_bets or 0
                ),
                "lost_bets": int(
                    row.lost_bets or 0
                ),
                "total_stake": float(
                    row.total_stake or 0
                ),
                "total_profit": float(
                    row.total_profit or 0
                ),
                "average_odd": float(
                    row.average_odd or 0
                ),
            }
            for row in rows
        ]

    def get_performance_by_competition(
        self,
    ) -> list[dict]:
        """
        Agrupa o desempenho por competição.
        """

        statement = (
            select(
                Competition.name.label(
                    "competition_name"
                ),

                Competition.season.label(
                    "season"
                ),

                func.count(Bet.id).label(
                    "total_bets"
                ),

                func.sum(
                    case(
                        (Bet.result == "won", 1),
                        else_=0,
                    )
                ).label("won_bets"),

                func.sum(
                    case(
                        (Bet.result == "lost", 1),
                        else_=0,
                    )
                ).label("lost_bets"),

                func.coalesce(
                    func.sum(Bet.stake_units),
                    0.0,
                ).label("total_stake"),

                func.coalesce(
                    func.sum(Bet.profit_units),
                    0.0,
                ).label("total_profit"),
            )
            .join(
                Match,
                Match.competition_id
                == Competition.id,
            )
            .join(
                Bet,
                Bet.match_id == Match.id,
            )
            .where(
                Bet.is_official.is_(True),
                Bet.status == "settled",
            )
            .group_by(
                Competition.id,
                Competition.name,
                Competition.season,
            )
            .order_by(
                Competition.name
            )
        )

        rows = self.session.execute(
            statement
        ).all()

        return [
            {
                "competition_name": (
                    row.competition_name
                ),
                "season": row.season,
                "total_bets": int(
                    row.total_bets or 0
                ),
                "won_bets": int(
                    row.won_bets or 0
                ),
                "lost_bets": int(
                    row.lost_bets or 0
                ),
                "total_stake": float(
                    row.total_stake or 0
                ),
                "total_profit": float(
                    row.total_profit or 0
                ),
            }
            for row in rows
        ]

    def get_profit_timeline(
        self,
    ) -> list[dict]:
        """
        Retorna as apostas liquidadas em ordem
        cronológica para calcular lucro acumulado.
        """

        statement = (
            select(
                Bet.id,
                Bet.settled_at,
                Bet.profit_units,
                Bet.selection,
            )
            .where(
                Bet.is_official.is_(True),
                Bet.status == "settled",
            )
            .order_by(
                Bet.settled_at,
                Bet.id,
            )
        )

        rows = self.session.execute(
            statement
        ).all()

        return [
            {
                "bet_id": row.id,
                "settled_at": row.settled_at,
                "profit_units": float(
                    row.profit_units or 0
                ),
                "selection": row.selection,
            }
            for row in rows
        ]