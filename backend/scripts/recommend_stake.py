from app.database.session import SessionLocal
from app.repositories import BankrollRepository
from app.services import RiskService


def main() -> None:
    session = SessionLocal()

    try:
        bankroll_repository = (
            BankrollRepository(session)
        )

        bankroll = (
            bankroll_repository.find_by_name(
                "Banca Principal"
            )
        )

        if not bankroll:
            print(
                "A Banca Principal não foi encontrada."
            )
            return

        service = RiskService(session)

        recommendation = (
            service.recommend_stake(
                bankroll_id=bankroll.id,
                probability=0.55,
                odd_value=2.10,
                profile_code="moderate",
            )
        )

        print("\nRECOMENDAÇÃO DE STAKE")
        print("=" * 50)

        print(
            f"Aprovada: "
            f"{recommendation['approved']}"
        )

        print(
            f"Perfil: "
            f"{recommendation['profile']}"
        )

        print(
            f"Motivo: "
            f"{recommendation['reason']}"
        )

        print(
            f"EV: "
            f"{recommendation['expected_value']:.2%}"
        )

        print(
            f"Stake recomendada: "
            f"R$ "
            f"{recommendation['stake_amount']:.2f}"
        )

        print(
            f"Percentual da banca: "
            f"{recommendation['stake_percentage']:.2f}%"
        )

        print(
            f"Stake em unidades: "
            f"{recommendation['stake_units']:.2f}u"
        )

    except Exception as error:
        print(
            f"Erro ao calcular stake: {error}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()