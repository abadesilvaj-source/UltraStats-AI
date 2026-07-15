from app.database.base import Base
from app.database.connection import engine
from app.models import Team


def create_tables() -> None:
    """Cria as tabelas que ainda não existem."""

    print("Criando tabelas do UltraStats AI...")

    Base.metadata.create_all(bind=engine)

    print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    create_tables()