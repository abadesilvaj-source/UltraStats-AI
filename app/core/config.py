import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """Configurações globais do UltraStats AI."""

    def __init__(self) -> None:
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://ultrastats:ultrastats123@localhost:5432/ultrastats_db",
        )

        self.postgres_user = os.getenv("POSTGRES_USER")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD")
        self.postgres_db = os.getenv("POSTGRES_DB")
        self.postgres_host = os.getenv("POSTGRES_HOST")
        self.postgres_port = os.getenv("POSTGRES_PORT")

        self.debug = True
        self.app_name = "UltraStats AI"
        self.version = "0.1.0"


settings = Settings()