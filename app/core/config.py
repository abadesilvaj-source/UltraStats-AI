import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configurações gerais do UltraStats AI."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://ultrastats:ultrastats123@localhost:5432/ultrastats_db",
    )


settings = Settings()