from app.database.session import SessionLocal
from app.services import PerformanceService


def main() -> None:
    session = SessionLocal()

    try:
        service = PerformanceService(session)

        summary = service.get_general_summary()

        print("\n" + "=" * 60)
        print("ULTRASTATS AI — PAINEL DE DESEMPENHO")
        print("=" * 60)

        print(
            f"Total de apostas: "
            f"{summary['total_bets']}"
        )

        print(
            f"Vitórias: "
            f"{summary['won_bets']}"
        )

        print(
            f"Derrotas: "
            f"{summary['lost_bets']}"
        )

        print(
            f"Anuladas: "
            f"{summary['void_bets']}"
        )

        print(
            f"Taxa de acerto: "
            f"{summary['win_rate']:.2f}%"
        )

        print(
            f"Stake total: "
            f"{summary['total_stake']:.2f}u"
        )

        print(
            f"Lucro acumulado: "
            f"{summary['total_profit']:.2f}u"
        )

        print(
            f"ROI: "
            f"{summary['roi']:.2f}%"
        )

        print(
            f"Odd média: "
            f"{summary['average_odd']:.2f}"
        )

        print(
            f"EV médio: "
            f"{summary['average_ev']:.2%}"
        )

        print("\nDesempenho por mercado:\n")

        markets = service.get_market_performance()

        for market in markets:
            print(
                f"- {market['market_name']} | "
                f"Apostas: {market['total_bets']} | "
                f"Lucro: "
                f"{market['total_profit']:.2f}u | "
                f"ROI: {market['roi']:.2f}%"
            )

        print("\nDesempenho por competição:\n")

        competitions = (
            service.get_competition_performance()
        )

        for competition in competitions:
            print(
                f"- "
                f"{competition['competition_name']} "
                f"{competition['season']} | "
                f"Apostas: "
                f"{competition['total_bets']} | "
                f"Lucro: "
                f"{competition['total_profit']:.2f}u | "
                f"ROI: "
                f"{competition['roi']:.2f}%"
            )

    except Exception as error:
        print(
            f"Erro ao gerar relatório: {error}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()