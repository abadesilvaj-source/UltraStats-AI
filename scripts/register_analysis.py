from app.database.session import SessionLocal
from app.services import AnalysisService


def main() -> None:
    session = SessionLocal()

    try:
        service = AnalysisService(session)

        odd, prediction, bet = service.register_analysis(
            match_external_id="test-palmeiras-flamengo-2026",
            market_code="over_2_5_goals",
            bookmaker="Casa de Teste",
            selection="Mais de 2.5 gols",
            odd_value=2.10,
            model_probability=0.55,
            model_version="0.1.0",
            confidence=78.0,
            uqs=82.0,
            use_score=80.0,
            confluence=75.0,
            evidence_level="B",
            risk_level="Médio",
            create_official_bet=True,
            stake_units=1.0,
        )

        print("\nAnálise registrada com sucesso!")

        print(
            f"Odd: {odd.odd_value} | "
            f"Casa: {odd.bookmaker}"
        )

        print(
            f"Probabilidade do modelo: "
            f"{prediction.probability:.2%}"
        )

        print(
            f"Probabilidade implícita: "
            f"{prediction.implied_probability:.2%}"
        )

        print(
            f"EV: "
            f"{prediction.expected_value:.2%}"
        )

        if bet:
            print(
                f"Aposta oficial criada | "
                f"ID: {bet.id} | "
                f"Stake: {bet.stake_units}u"
            )
        else:
            print("Nenhuma aposta oficial foi criada.")

    except Exception as error:
        print(f"Erro ao registrar análise: {error}")

    finally:
        session.close()


if __name__ == "__main__":
    main()