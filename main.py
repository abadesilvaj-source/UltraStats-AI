from sqlalchemy import text

from app.database.connection import engine


def check_database_connection() -> bool:
    """Verifica se o PostgreSQL está acessível."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

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