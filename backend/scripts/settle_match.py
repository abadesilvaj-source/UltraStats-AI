from app.database.session import SessionLocal
from app.services import PostMatchService


def main() -> None:
    session = SessionLocal()

    try:
        service = PostMatchService(session)

        result = service.settle_match(
            match_external_id=(
                "test-palmeiras-flamengo-2026"
            ),
            home_score=2,
            away_score=1,
            source="Fonte oficial de teste",
            corners_home=6,
            corners_away=4,
            yellow_cards_home=2,
            yellow_cards_away=3,
            red_cards_home=0,
            red_cards_away=0,
            shots_home=14,
            shots_away=11,
            shots_on_target_home=6,
            shots_on_target_away=4,
            offsides_home=2,
            offsides_away=1,
            possession_home=54.0,
            possession_away=46.0,
            xg_home=1.75,
            xg_away=1.10,
        )

        match = result["match"]
        statistics = result["statistics"]
        settled_bets = result["settled_bets"]
        total_profit = result["total_profit_units"]

        print("\nPartida encerrada com sucesso!")

        print(
            f"Placar: "
            f"{match.home_score} x {match.away_score}"
        )

        print(
            f"Escanteios: "
            f"{statistics.corners_home} x "
            f"{statistics.corners_away}"
        )

        print(
            f"Cartões amarelos: "
            f"{statistics.yellow_cards_home} x "
            f"{statistics.yellow_cards_away}"
        )

        print(
            f"Apostas liquidadas: "
            f"{len(settled_bets)}"
        )

        for bet in settled_bets:
            print(
                f"\nAposta ID: {bet.id}"
                f"\nSeleção: {bet.selection}"
                f"\nResultado: {bet.result}"
                f"\nLucro/prejuízo: "
                f"{bet.profit_units:.2f}u"
            )

        print(
            f"\nLucro total da partida: "
            f"{total_profit:.2f}u"
        )

    except Exception as error:
        print(f"Erro ao encerrar partida: {error}")

    finally:
        session.close()


if __name__ == "__main__":
    main()