from sqlalchemy import text

from app.database.engine import engine


def check_database_connection() -> bool:
    """Verifica se o PostgreSQL está acessível."""

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.scalar()

        print("Banco de dados conectado com sucesso!")
        return True

    except Exception as error:
        print(f"Erro ao conectar ao banco de dados: {error}")
        return False


def main() -> None:
    print("=" * 50)
    print("UltraStats AI iniciado com sucesso!")
    print("=" * 50)

    check_database_connection()


if __name__ == "__main__":
    main()