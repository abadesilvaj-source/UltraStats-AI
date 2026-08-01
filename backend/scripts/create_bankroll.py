from app.database.session import SessionLocal
from app.services import BankrollService


def main() -> None:
    session = SessionLocal()

    try:
        service = BankrollService(session)

        bankroll = service.create_bankroll(
            name="Banca Principal",
            initial_balance=1000.00,
            currency="BRL",
            unit_percentage=1.0,
        )

        unit_value = (
            service.calculate_unit_value(
                bankroll.id
            )
        )

        print("\nBanca criada com sucesso!")

        print(
            f"ID: {bankroll.id}"
        )

        print(
            f"Nome: {bankroll.name}"
        )

        print(
            f"Saldo inicial: "
            f"R$ {bankroll.initial_balance}"
        )

        print(
            f"Saldo atual: "
            f"R$ {bankroll.current_balance}"
        )

        print(
            f"Percentual por unidade: "
            f"{bankroll.unit_percentage:.2f}%"
        )

        print(
            f"Valor atual de 1 unidade: "
            f"R$ {unit_value:.2f}"
        )

    except Exception as error:
        print(
            f"Erro ao criar banca: {error}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()