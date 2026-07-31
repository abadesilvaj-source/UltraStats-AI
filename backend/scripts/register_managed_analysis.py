from app.database.session import SessionLocal
from app.repositories import BankrollRepository
from app.services import (
    AnalysisService,
    RiskService,
)


def main() -> None:
    session = SessionLocal()

    try:
        bankroll = (
            BankrollRepository(session)
            .find_by_name("Banca Principal")
        )

        if not bankroll:
            print("Banca não encontrada.")
            return

        probability = 0.55
        odd_value = 2.10

        risk_service = RiskService(session)

        recommendation = (
            risk_service.recommend_stake(
                bankroll_id=bankroll.id,
                probability=probability,
                odd_value=odd_value,
                profile_code="moderate",
            )
        )

        if not recommendation["approved"]:
            print(
                "Aposta rejeitada pelo risco: "
                f"{recommendation['reason']}"
            )
            return

        analysis_service = (
            AnalysisService(session)
        )

        odd, prediction, bet = (
            analysis_service.register_analysis(
                match_external_id=(
                    "test-palmeiras-flamengo-2026"
                ),
                market_code="over_2_5_goals",
                bookmaker="Casa de Teste",
                selection="Mais de 2.5 gols",
                odd_value=odd_value,
                model_probability=probability,
                model_version="0.2.0",
                confidence=78.0,
                uqs=82.0,
                use_score=80.0,
                confluence=75.0,
                evidence_level="B",
                risk_level="Médio",
                create_official_bet=True,
                stake_units=(
                    recommendation[
                        "stake_units"
                    ]
                ),
                bankroll_id=bankroll.id,
                stake_amount=(
                    recommendation[
                        "stake_amount"
                    ]
                ),
            )
        )

        print("\nAposta gerenciada criada!")

        print(
            f"Bet ID: {bet.id}"
        )

        print(
            f"Stake: "
            f"R$ {bet.stake_amount}"
        )

        print(
            f"Unidades: "
            f"{bet.stake_units:.2f}u"
        )

        session.refresh(bankroll)

        print(
            f"Saldo restante: "
            f"R$ {bankroll.current_balance}"
        )

    except Exception as error:
        session.rollback()

        print(
            f"Erro ao registrar aposta: {error}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()